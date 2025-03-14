import * as React from "react"
import * as DropdownMenuPrimitive from "@radix-ui/react-dropdown-menu"
import {
  CheckIcon,
  ChevronRightIcon,
  DotFilledIcon,
} from "@radix-ui/react-icons"

import { cn } from "@/lib/utils"

const DropdownMenu = DropdownMenuPrimitive.Root

const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger

const DropdownMenuGroup = DropdownMenuPrimitive.Group

const DropdownMenuPortal = DropdownMenuPrimitive.Portal

const DropdownMenuSub = DropdownMenuPrimitive.Sub

const DropdownMenuRadioGroup = DropdownMenuPrimitive.RadioGroup

const DropdownMenuSubTrigger = React.forwardRef(({ className, inset, children, ...props }, ref) => (
  <DropdownMenuPrimitive.SubTrigger
    ref={ref}
    className={cn(
      "o-flex o-cursor-default o-gap-2 o-select-none o-items-center o-rounded-sm o-px-2 o-py-1.5 o-text-sm o-outline-none focus:o-bg-accent data-[state=open]:o-bg-accent [&_svg]:o-pointer-events-none [&_svg]:o-size-4 [&_svg]:o-shrink-0",
      inset && "o-pl-8",
      className
    )}
    {...props}>
    {children}
    <ChevronRightIcon className="o-ml-auto" />
  </DropdownMenuPrimitive.SubTrigger>
))
DropdownMenuSubTrigger.displayName =
  DropdownMenuPrimitive.SubTrigger.displayName

const DropdownMenuSubContent = React.forwardRef(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.SubContent
    ref={ref}
    className={cn(
      "o-z-50 o-min-w-[8rem] o-overflow-hidden o-rounded-md o-border o-bg-popover o-p-1 o-text-popover-foreground o-shadow-lg data-[state=open]:o-animate-in data-[state=closed]:o-animate-out data-[state=closed]:o-fade-out-0 data-[state=open]:o-fade-in-0 data-[state=closed]:o-zoom-out-95 data-[state=open]:o-zoom-in-95 data-[side=bottom]:o-slide-in-from-top-2 data-[side=left]:o-slide-in-from-right-2 data-[side=right]:o-slide-in-from-left-2 data-[side=top]:o-slide-in-from-bottom-2",
      className
    )}
    {...props} />
))
DropdownMenuSubContent.displayName =
  DropdownMenuPrimitive.SubContent.displayName

const DropdownMenuContent = React.forwardRef(({ className, sideOffset = 4, ...props }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        "o-z-50 o-min-w-[8rem] o-overflow-hidden o-rounded-md o-border o-bg-popover o-p-1 o-text-popover-foreground o-shadow-md",
        "data-[state=open]:o-animate-in data-[state=closed]:o-animate-out data-[state=closed]:o-fade-out-0 data-[state=open]:o-fade-in-0 data-[state=closed]:o-zoom-out-95 data-[state=open]:o-zoom-in-95 data-[side=bottom]:o-slide-in-from-top-2 data-[side=left]:o-slide-in-from-right-2 data-[side=right]:o-slide-in-from-left-2 data-[side=top]:o-slide-in-from-bottom-2",
        className
      )}
      {...props} />
  </DropdownMenuPrimitive.Portal>
))
DropdownMenuContent.displayName = DropdownMenuPrimitive.Content.displayName

const DropdownMenuItem = React.forwardRef(({ className, inset, ...props }, ref) => (
  <DropdownMenuPrimitive.Item
    ref={ref}
    className={cn(
      "o-relative o-flex o-cursor-default o-select-none o-items-center o-gap-2 o-rounded-sm o-px-2 o-py-1.5 o-text-sm o-outline-none o-transition-colors focus:o-bg-accent focus:o-text-accent-foreground data-[disabled]:o-pointer-events-none data-[disabled]:o-opacity-50 [&>svg]:o-size-4 [&>svg]:o-shrink-0",
      inset && "o-pl-8",
      className
    )}
    {...props} />
))
DropdownMenuItem.displayName = DropdownMenuPrimitive.Item.displayName

const DropdownMenuCheckboxItem = React.forwardRef(({ className, children, checked, ...props }, ref) => (
  <DropdownMenuPrimitive.CheckboxItem
    ref={ref}
    className={cn(
      "o-relative o-flex o-cursor-default o-select-none o-items-center o-rounded-sm o-py-1.5 o-pl-8 o-pr-2 o-text-sm o-outline-none o-transition-colors focus:o-bg-accent focus:o-text-accent-foreground data-[disabled]:o-pointer-events-none data-[disabled]:o-opacity-50",
      className
    )}
    checked={checked}
    {...props}>
    <span
      className="o-absolute o-left-2 o-flex o-h-3.5 o-w-3.5 o-items-center o-justify-center">
      <DropdownMenuPrimitive.ItemIndicator>
        <CheckIcon className="o-h-4 o-w-4" />
      </DropdownMenuPrimitive.ItemIndicator>
    </span>
    {children}
  </DropdownMenuPrimitive.CheckboxItem>
))
DropdownMenuCheckboxItem.displayName =
  DropdownMenuPrimitive.CheckboxItem.displayName

const DropdownMenuRadioItem = React.forwardRef(({ className, children, ...props }, ref) => (
  <DropdownMenuPrimitive.RadioItem
    ref={ref}
    className={cn(
      "o-relative o-flex o-cursor-default o-select-none o-items-center o-rounded-sm o-py-1.5 o-pl-8 o-pr-2 o-text-sm o-outline-none o-transition-colors focus:o-bg-accent focus:o-text-accent-foreground data-[disabled]:o-pointer-events-none data-[disabled]:o-opacity-50",
      className
    )}
    {...props}>
    <span
      className="o-absolute o-left-2 o-flex o-h-3.5 o-w-3.5 o-items-center o-justify-center">
      <DropdownMenuPrimitive.ItemIndicator>
        <DotFilledIcon className="o-h-4 o-w-4 o-fill-current" />
      </DropdownMenuPrimitive.ItemIndicator>
    </span>
    {children}
  </DropdownMenuPrimitive.RadioItem>
))
DropdownMenuRadioItem.displayName = DropdownMenuPrimitive.RadioItem.displayName

const DropdownMenuLabel = React.forwardRef(({ className, inset, ...props }, ref) => (
  <DropdownMenuPrimitive.Label
    ref={ref}
    className={cn("o-px-2 o-py-1.5 o-text-sm o-font-semibold", inset && "o-pl-8", className)}
    {...props} />
))
DropdownMenuLabel.displayName = DropdownMenuPrimitive.Label.displayName

const DropdownMenuSeparator = React.forwardRef(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Separator
    ref={ref}
    className={cn("o--mx-1 o-my-1 o-h-px o-bg-muted", className)}
    {...props} />
))
DropdownMenuSeparator.displayName = DropdownMenuPrimitive.Separator.displayName

const DropdownMenuShortcut = ({
  className,
  ...props
}) => {
  return (
    (<span
      className={cn("o-ml-auto o-text-xs o-tracking-widest o-opacity-60", className)}
      {...props} />)
  );
}
DropdownMenuShortcut.displayName = "DropdownMenuShortcut"

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuRadioGroup,
}
