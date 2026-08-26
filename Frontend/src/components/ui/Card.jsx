import { forwardRef } from 'react';
import { cn } from '../../lib/utils';

const Card = forwardRef(function Card({ className, ...props }, ref) {
  return (
    <div
      ref={ref}
      className={cn(
        'bg-surface border border-line rounded-xl shadow-xs',
        className,
      )}
      {...props}
    />
  );
});

const CardHeader = forwardRef(function CardHeader({ className, ...props }, ref) {
  return <div ref={ref} className={cn('px-5 py-4 border-b border-line', className)} {...props} />;
});

const CardTitle = forwardRef(function CardTitle({ className, ...props }, ref) {
  return <h3 ref={ref} className={cn('text-[15px] font-semibold text-text', className)} {...props} />;
});

const CardDescription = forwardRef(function CardDescription({ className, ...props }, ref) {
  return <p ref={ref} className={cn('text-[13px] text-text-muted mt-0.5', className)} {...props} />;
});

const CardContent = forwardRef(function CardContent({ className, ...props }, ref) {
  return <div ref={ref} className={cn('p-5', className)} {...props} />;
});

const CardFooter = forwardRef(function CardFooter({ className, ...props }, ref) {
  return (
    <div
      ref={ref}
      className={cn('px-5 py-3.5 border-t border-line bg-surface-sunken rounded-b-xl', className)}
      {...props}
    />
  );
});

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };
