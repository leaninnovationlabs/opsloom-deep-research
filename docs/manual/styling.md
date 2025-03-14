# Styling
Opsloom makes it easy to style your assistants to suit you or your company's needs. To customize an account's style, submit a `palette` object in the body of the `/account` POST request. `palette` allows you to define custom CSS properties for a given account in both light and dark mode. You can find details on available properties in the table below.

---

| Property | Values Accepted | Default Value |
| -------- | ------- | ------- |
| background | HSL | 53 100% 95% |
| foreground | HSL | 53 5% 10% |
| card | HSL | 53 50% 90% |
| card_foreground | HSL | 53 5% 15% |
| popover | HSL | 53 100% 95% |
| popover_foreground | HSL | 53 100% 10% |
| primary | HSL | 53 57% 20% |
| primary_foreground | HSL | 0 0% 100% |
| secondary | HSL | 53 30% 70% |
| secondary_foreground | HSL | 0 0% 0% |
| muted | HSL | 15 30% 85% |
| muted_foreground | HSL | 53 5% 40% |
| accent | HSL | 15 30% 80% |
| accent_foreground | HSL | 53 5% 15% |
| destructive | HSL | 0 100% 40% |
| destructive_foreground | HSL | 53 5% 90% |
| border | HSL | 53 30% 50% |
| input | HSL | 53 30% 40% |
| ring | HSL | 53 57% 20% |
| radius | REM | 0.5rem |
