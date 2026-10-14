import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  onClick,
  hoverable = false,
}) => {
  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 rounded-2xl p-4 sm:p-5 shadow-sm transition-all duration-150 ${
        hoverable ? 'hover:shadow-md hover:border-emerald-300 dark:hover:border-emerald-700/60 cursor-pointer hover:-translate-y-0.5' : ''
      } ${className}`}
    >
      {children}
    </div>
  );
};
