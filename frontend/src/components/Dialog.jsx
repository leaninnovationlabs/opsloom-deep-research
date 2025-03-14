import { useEffect, useState, useId, forwardRef } from "react"
import { Button } from "@/components/ui/button"
import {
    Dialog as RadixDialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import useAppConfigStore from "@/lib/store/appconfig.store"
import useUserStore from "@/lib/store/user.store"
import { cn, validateEmail } from "@/lib/utils"
import { useShallow } from "zustand/react/shallow";
import { produce } from "immer";
import useLogin from "@/lib/store/hooks/useLogin.hook"
import useSignup from "@/lib/store/hooks/useSignup.hook"

const Dialog = {}

const INIT = {
    email: "",
    password: "",
    confirmPassword: ""
}

const MODES = {
    SIGN_UP: "SIGN_UP",
    LOGIN: "LOGIN"
}

const Welcome = () => {
    const [mode, setMode] = useState(MODES.LOGIN)
    const [open, setOpen] = useState();
    const [state, setState] = useState(INIT);
    const [errors, setErrors] = useState(INIT);
    const [loading, setLoading] = useState(false);

    const loggedIn = useUserStore(state => state.loggedIn);
    const [login] = useLogin();
    const [signUp] = useSignup();
    
    const [requiresEmail] = useAppConfigStore(useShallow(state => [state.requiresEmail, state.shortCode]))


    useEffect(() => {
        if (loggedIn === false && requiresEmail === true) {
            setOpen(true)
        }
        else if (loggedIn === true) {
            setOpen(false)
        }
    }, [loggedIn, requiresEmail])

    useEffect(() => {
        setState(produce(draft => { draft.password = ""; draft.confirmPassword = "" }))
        setErrors(INIT)
    }, [mode])

    const onOpenChange = () => {
        if (!loggedIn) {
            return
        }
        setOpen(x => !x)
    }

    function validate() {
        if (!state.email || state.email.length === 0) {
            setErrors(produce(draft => { draft.email = "Email is required" }))
            return false;
        }
        if (!validateEmail(state.email)) {
            setErrors(produce(draft => { draft.email = "Please enter a valid email" }))
            return false;
        }
        if (!state.password || state.password.length === 0) {
            setErrors(produce(draft => { draft.password = "Password is required" }))
            return false;
        }
        // if (state.password !== state.confirmPassword) {
        //     setErrors(produce(draft => { draft.confirmPassword = "Passwords don't match" }))
        //     return false;
        // }
        return true;
    }

    const onSubmit = async (e) => {
        e.preventDefault();
        setErrors(INIT)
        if (validate()) {
            setLoading(true)
            try {
                if (mode === MODES.SIGN_UP) {
                    await signUp({ email: state.email, password: state.password });
                }
                else {
                    await login({ email: state.email, password: state.password });
                }
                setOpen(false)
                setState(produce(draft => { draft.password = "" }))
            }
            catch (err) {
                setErrors(produce(draft => { draft.password = err.message }))
            }
            finally {
                setLoading(false)
            }
        }
    }

    return (
        <RadixDialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="sm:o-max-w-[425px]" x={false}>
                <DialogHeader>
                    <DialogTitle>
                        {mode === MODES.SIGN_UP ?
                            "Sign Up" :
                            "Login"}
                    </DialogTitle>
                    <DialogDescription>
                        {mode === MODES.SIGN_UP ? "Please provide some info before using this chatbot." : "Welcome Back. Please provide your login credentials."}
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={onSubmit}>


                    <div className="o-grid o-gap-5 o-pt-2 o-pb-6">

                        <LabeledInput
                            label="Email"
                            id="email"
                            type="email"

                            placeholder="your@e.mail"
                            disabled={loading}
                            value={state.email}
                            onChange={(e) => setState(produce(draft => { draft.email = e.target.value }))}
                            error={errors.email}
                        />

                        <LabeledInput
                            label="Password"
                            id="password"
                            type="password"
                            autoComplete="off"
                            disabled={loading}
                            value={state.password}
                            onChange={(e) => setState(produce(draft => { draft.password = e.target.value }))}
                            error={errors.password}
                        />

                        {/* {mode === MODES.SIGN_UP &&
                            <LabeledInput
                                label="Confirm"
                                type="password"
                                autoComplete="off"
                                disabled={loading}
                                value={state.confirmPassword}
                                onChange={(e) => setState(produce(draft => { draft.confirmPassword = e.target.value }))}
                                error={errors.confirmPassword}
                            />

                        } */}


                    </div>
                    <DialogFooter>

                        {mode === MODES.SIGN_UP &&
                            <>
                                <Button variant="link" type="button" disabled={loading} onClick={() => setMode(MODES.LOGIN)}>Or Log in</Button>
                                <Button type="submit" disabled={loading}>Sign Up</Button>
                            </>
                        }
                        {mode === MODES.LOGIN &&
                            <>
                                <Button variant="link" type="button" disabled={loading} onClick={() => setMode(MODES.SIGN_UP)}>Or Sign Up</Button>
                                <Button type="submit" disabled={loading}>Login</Button>
                            </>
                        }
                    </DialogFooter>
                </form>
            </DialogContent>
        </RadixDialog>
    )
}




const LabeledInput = forwardRef(({ className, id, label = "Field", error = "", ...props }, ref) => {
    const _id = useId()
    return (
        (
            <div className="o-grid o-grid-cols-10 o-items-center o-gap-4">
                <Label htmlFor={id ?? _id} className="o-text-right o-col-span-3">
                    {label}
                </Label>
                <div className="o-relative o-col-span-7">
                    <Input
                        id={id ?? _id}
                        className={cn(
                            error.length && "o-border-[red]",
                            className
                        )}
                        ref={ref}
                        {...props} />
                    {error && error?.length &&
                        <div className="o-absolute -o-bottom-7 o-left-1 o-flex o-items-start o-h-[24px]">
                            <p className="o-text-[red] o-text-xs o-leading-[1em]">
                                {error}
                            </p>
                        </div>

                    }
                </div>
            </div>
        )
    );
})
Input.displayName = "Input"

export { Input }


Dialog.displayName = "Dialog";
Dialog.Welcome = Welcome;

export default Dialog;