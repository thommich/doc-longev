import React, {type CSSProperties, type ReactNode} from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

export type BadgeVariant =
  | 'default'
  | 'info'
  | 'success'
  | 'warning'
  | 'danger'
  | 'purple';

export type BadgeSize = 'sm' | 'md' | 'lg';

export type BadgeProps = {
  /** The content displayed inside the badge. */
  children: ReactNode;
  /** Semantic color treatment. */
  variant?: BadgeVariant;
  /** Controls the badge's text and spacing. */
  size?: BadgeSize;
  /** Optional leading icon or other inline React node. */
  icon?: ReactNode;
  /** Adds a small status dot before the content. */
  dot?: boolean;
  /** Gives the badge fully rounded ends. */
  pill?: boolean;
  className?: string;
  style?: CSSProperties;
};

export default function Badge({
  children,
  variant = 'default',
  size = 'md',
  icon,
  dot = false,
  pill = false,
  className,
  style,
}: BadgeProps): React.JSX.Element {
  return (
    <span
      className={clsx(
        styles.badge,
        styles[variant],
        styles[size],
        pill && styles.pill,
        className,
      )}
      style={style}
    >
      {dot && <span className={styles.dot} aria-hidden="true" />}
      {icon && <span className={styles.icon}>{icon}</span>}
      <span>{children}</span>
    </span>
  );
}
