import type { ButtonHTMLAttributes, ReactNode } from 'react'

interface FAQRowProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  question: ReactNode
  expanded?: boolean
  children?: ReactNode
}

/**
 * Monad FAQ row — full width, 40px vertical padding, 1px Ash BOTTOM border only.
 * Question in serif 24px/400 Off-Black; trailing chevron ↓ 20px right-aligned.
 */
export function FAQRow({
  question,
  expanded = false,
  children,
  className = '',
  ...rest
}: FAQRowProps) {
  return (
    <div className={`border-b border-ash ${className}`}>
      <button
        type="button"
        className="flex w-full cursor-pointer items-center justify-between bg-transparent py-10 text-left"
        {...rest}
      >
        <span className="font-heading text-subheading tracking-subheading leading-subheading text-off-black">
          {question}
        </span>
        <span
          aria-hidden="true"
          className={`text-body text-off-black transition-transform ${expanded ? 'rotate-180' : ''}`}
        >
          ↓
        </span>
      </button>
      {expanded && children && (
        <div className="pb-10 font-mono text-body tracking-body leading-body text-graphite">
          {children}
        </div>
      )}
    </div>
  )
}
