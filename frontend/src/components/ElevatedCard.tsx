import type { HTMLAttributes, ReactNode } from 'react'

interface ElevatedCardProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
  title?: ReactNode
  body?: ReactNode
  children?: ReactNode
}

/**
 * Monad ElevatedCard — Periwinkle Mist fill, 40px radius, 40px padding.
 * The ONLY card allowed a colored surface fill (rule 8's exception).
 */
export function ElevatedCard({
  title,
  body,
  children,
  className = '',
  ...rest
}: ElevatedCardProps) {
  return (
    <div className={`rounded-cards bg-periwinkle-mist p-10 ${className}`} {...rest}>
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
