from datetime import datetime
from pydantic_ai import RunContext, ModelRetry
from typing import Literal
from .schemas import (
    GuestSchema,
    ReservationSchema,
    ServiceSchema,
    ServiceOrderSchema,
    CreateReservationRequest
)

def register_agent_tools(agent, gateway):
    """
    Register the 'tools' used by the agent.

    The agent references these tools when it needs to create, retrieve, update,
    or delete reservations/services via the `HotelApiClient`.
    """

    # ----------------------------------------------
    # Internal Helper: Convert datetime -> isoformat
    # ----------------------------------------------

    def _ensure_iso_str(val):
        """
        Convert Python datetime objects to isoformat strings, 
        otherwise return val unchanged.
        """
        if isinstance(val, datetime):
            return val.isoformat()
        return val

    @agent.system_prompt
    async def get_current_user():
        """
        System prompt automatically providing context (guest info, available services, reservations).

        1. Ensures `gateway.guest` is set, defaulting to a test user if undefined.
        2. Fetches the list of all services if not already cached.
        3. Fetches the list of reservations for this guest if not already cached.

        Returns:
            str: A short system prompt summarizing the relevant data for the LLM.
        """
        # if not gateway.guest:
        #     gateway.guest = GuestSchema(
        #         guest_id=123,
        #         full_name="Test Guest",
        #         email="guest@example.com"
        #     )

        if not gateway.available_services:
            gateway.available_services = await gateway.api_client.list_all_services()

        if not gateway.reservations and gateway.guest:
            gateway.reservations = await gateway.api_client.get_reservations_for_guest(
                gateway.guest.guest_id
            )

        return (
            f"You are a hotel AI assistant for WhipSplash. "
            f"Available services: {gateway.available_services}. "
            f"Guest info: {gateway.guest}. "
            f"Current reservations: {gateway.reservations}. "
            f"Always create plans before confirming them with the guest. Send these plans to the guest for confirmation."
            f"When you make a plan, set the type of the response model to 'dialog' and be sure to include the fields 'title' and 'description' in response_metadata."
            f"For all other responses, set the type of the response model to 'text'"
            f"Respond courteously and professionally."
        )

    @agent.tool
    async def list_all_services(ctx: RunContext[GuestSchema]) -> list[ServiceSchema]:
        """Retrieve a list of all available services (GET /services)."""
        services = await gateway.api_client.list_all_services()
        gateway.available_services = services
        return services

    @agent.tool
    async def get_reservations(ctx: RunContext[GuestSchema]) -> list[ReservationSchema]:
        """Retrieve reservations for the current guest (GET /reservations/{guest_id})."""
        return await gateway.api_client.get_reservations_for_guest(gateway.guest.guest_id)

    @agent.tool
    async def create_reservation_plan(
        ctx: RunContext[GuestSchema],
        room_type: Literal["single", "double", "suite"],
        check_in: datetime,
        check_out: datetime
    ) -> str:
        """
        Prepare a plan for creating a new reservation (no API call yet).
        """
        gateway._pending_reservation_info = {
            "room_type": room_type,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat()
        }
        return (
            CreateReservationRequest(
                guest_id=gateway.guest.guest_id,
                full_name = "Peter Griffin",
                email = gateway.guest.email,
                room_type=room_type,
                check_in=check_in,
                check_out=check_out
            )
        )

    @agent.tool
    async def create_reservation(ctx: RunContext[GuestSchema]) -> ReservationSchema:
        """
        Confirm & create a new reservation using the stored plan in _pending_reservation_info (POST /reservations).
        """
        if not gateway._pending_reservation_info:
            raise ModelRetry("No pending reservation info found to confirm.")

        info = gateway._pending_reservation_info

        # Ensure check_in/check_out are ISO strings
        check_in_str = _ensure_iso_str(info.get("check_in"))
        check_out_str = _ensure_iso_str(info.get("check_out"))

        new_res = await gateway.api_client.create_reservation(
            CreateReservationRequest(
                guest_id=gateway.guest.guest_id,
                full_name=gateway.guest.full_name,
                email=gateway.guest.email,
                room_type=info["room_type"],
                check_in=check_in_str,
                check_out=check_out_str,
            )
        )

        gateway._pending_reservation_info = None
        gateway.reservations.append(new_res)
        return new_res

    @agent.tool
    async def modify_reservation_plan(
        ctx: RunContext[GuestSchema],
        reservation_id: int,
        new_check_in: datetime = None,
        new_check_out: datetime = None,
        new_room_type: str = None
    ) -> str:
        """
        Prepare changes to an existing reservation (no API call yet).
        """
        gateway._pending_modification_info = {
            "reservation_id": reservation_id,
            "check_in": new_check_in.isoformat() if new_check_in else None,
            "check_out": new_check_out.isoformat() if new_check_out else None,
            "room_type": new_room_type
        }

        plan_text = f"Plan to modify reservation {reservation_id}:\n"
        if new_check_in:
            plan_text += f"- New check-in: {new_check_in}\n"
        if new_check_out:
            plan_text += f"- New check-out: {new_check_out}\n"
        if new_room_type:
            plan_text += f"- New room type: {new_room_type}\n"
        plan_text += "Use modify_reservation() to confirm these changes."

        return plan_text

    @agent.tool
    async def modify_reservation(ctx: RunContext[GuestSchema]) -> ReservationSchema:
        """
        Confirm and apply changes to an existing reservation (PATCH /reservations/{reservation_id}).
        """
        if not gateway._pending_modification_info:
            raise ModelRetry("No pending modification info found to confirm.")

        data = gateway._pending_modification_info
        reservation_id = data["reservation_id"]

        # Convert any datetime objects if present
        check_in_str = _ensure_iso_str(data.get("check_in"))
        check_out_str = _ensure_iso_str(data.get("check_out"))

        updated_res = await gateway.api_client.modify_reservation(
            reservation_id=reservation_id,
            check_in=check_in_str,
            check_out=check_out_str,
            room_type=data["room_type"]
        )

        gateway._pending_modification_info = None

        for i, r in enumerate(gateway.reservations):
            if r.reservation_id == reservation_id:
                gateway.reservations[i] = updated_res
                break

        return updated_res

    @agent.tool
    async def cancel_reservation(ctx: RunContext[GuestSchema], reservation_id: int) -> bool:
        """Cancel a reservation by ID (DELETE /reservations/{reservation_id})."""
        success = await gateway.api_client.cancel_reservation(reservation_id)
        if success:
            gateway.reservations = [r for r in gateway.reservations if r.reservation_id != reservation_id]
        return success

    @agent.tool
    async def create_service_order(
        ctx: RunContext[GuestSchema],
        reservation_id: int,
        service_id: int,
        quantity: int,
        status: str = "pending"
    ) -> ServiceOrderSchema:
        """
        Create a new service order for a given reservation (POST /serviceorders).
        """
        return await gateway.api_client.create_service_order(reservation_id, service_id, quantity, status)

    @agent.tool
    async def list_service_orders_for_reservation(
        ctx: RunContext[GuestSchema],
        reservation_id: int
    ) -> list[ServiceOrderSchema]:
        """
        Retrieve all service orders for a specific reservation (GET /serviceorders/by_reservation/{reservation_id}).
        """
        return await gateway.api_client.list_service_orders_for_reservation(reservation_id)

    @agent.tool
    async def delete_service_order(
        ctx: RunContext[GuestSchema],
        order_id: int
    ) -> bool:
        """Delete a single service order (DELETE /serviceorders/{order_id})."""
        return await gateway.api_client.delete_service_order(order_id)

    @agent.tool
    async def delete_service_orders_for_reservation(
        ctx: RunContext[GuestSchema],
        reservation_id: int
    ) -> bool:
        """
        Delete all service orders for a given reservation (DELETE /serviceorders/for_reservation/{reservation_id}).
        """
        return await gateway.api_client.delete_service_orders_for_reservation(reservation_id)