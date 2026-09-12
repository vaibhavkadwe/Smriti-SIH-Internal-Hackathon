import type { HTMLAttributes, ReactNode } from 'react'

interface PillTagProps extends HTMLAttributes<HTMLSpanElement> {
  icon?: ReactNode
  children: ReactNode
}

/**
 * Monad PillTag — parchment fill, 1px Ash border, 9999px radius,
 * 12px 20px padding, 12px icon + 14px mono uppercase text.
 */
export function PillTag({ icon, children, className = '', ...rest }: PillTagProps) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-tags border border-ash bg-parchment px-5 py-3 font-mono text-body-sm uppercase tracking-body-sm leading-body-sm text-off-black ${className}`}
      {...rest}
    >
      {icon && <span aria-hidden="true" className="text-caption">{icon}</span>}
      {children}
    </span>
  )
}
