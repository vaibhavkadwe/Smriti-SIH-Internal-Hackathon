import type { ButtonHTMLAttributes, ReactNode } from 'react'

export type PillVariant = 'primary' | 'secondary' | 'ghost'

interface PillButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant: PillVariant
  children: ReactNode
  /** Primary CTA only: trailing ▸ arrow. Exactly one primary per screen. */
  arrow?: boolean
}

/**
 * Monad pill buttons — 100px radius, mono 14px UPPERCASE, 16px 32px padding.
 *
 * primary:   Lake Blue fill, white text, trailing ▸ (the ONLY lake-blue
 *            element on a screen — rule 5).
 * secondary: Off-Black fill, white text.
 * ghost:     transparent, 1px Off-Black border, Off-Black text.
 */
export function PillButton({
  variant,
  arrow = false,
  children,
  className = '',
  ...rest
}: PillButtonProps) {
  const styles: Record<PillVariant, string> = {
    primary: 'bg-lake-blue text-white hover:bg-[#1f49b3]',
    secondary: 'bg-off-black text-white hover:bg-[#363535]',
    ghost:
      'bg-transparent text-off-black border border-off-black hover:bg-off-black/5',
  }

  return (
    <button
      type="button"
      className={`no-select inline-flex min-h-12 cursor-pointer items-center justify-center gap-2 rounded-buttons px-8 py-4 font-mono text-body-sm uppercase tracking-body-sm leading-body-sm transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${styles[variant]} ${className}`}
      {...rest}
    >
      {children}
      {arrow && <span aria-hidden="true">▸</span>}
    </button>
  )
}
