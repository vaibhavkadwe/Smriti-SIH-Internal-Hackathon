import type { AnchorHTMLAttributes, ReactNode } from 'react'

interface TextLinkArrowProps extends AnchorHTMLAttributes<HTMLAnchorElement> {
  children: ReactNode
}

/** Monad text link — transparent, mono 14px, trailing → in Off-Black. */
export function TextLinkArrow({ children, className = '', ...rest }: TextLinkArrowProps) {
  return (
    <a
      className={`inline-flex cursor-pointer items-center gap-2 bg-transparent font-mono text-body-sm tracking-body-sm leading-body-sm text-off-black uppercase no-underline transition-opacity hover:opacity-70 ${className}`}
      {...rest}
    >
      {children}
      <span aria-hidden="true">→</span>
    </a>
  )
}
