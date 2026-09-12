import type { HTMLAttributes, ReactNode } from 'react'

interface FeatureCardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  /** Small mono glyph shown top-left — keep it an icon character or short emoji. */
  icon?: ReactNode
  title?: ReactNode
  body?: ReactNode
  children?: ReactNode
}

/**
 * Monad FeatureCard — 1px Ash border, 40px radius, 40px padding, NO shadow.
 * Title serif 24px/400 Off-Black; body mono 16px Graphite.
 */
export function FeatureCard({
  icon,
  title,
  body,
  children,
  className = '',
  ...rest
}: FeatureCardProps) {
  return (
    <div
      className={`rounded-cards border border-ash bg-parchment p-10 ${className}`}
      {...rest}
    >
      {icon && (
        <div aria-hidden="true" className="mb-4 font-mono text-body text-off-black">
          {icon}
        </div>
      )}
      {title && (
        <div className="font-heading text-subheading tracking-subheading leading-subheading text-off-black">
          {title}
        </div>
      )}
      {body && (
        <div className="mt-4 font-mono text-body tracking-body leading-body text-graphite">
          {body}
        </div>
      )}
      {children}
    </div>
  )
}
