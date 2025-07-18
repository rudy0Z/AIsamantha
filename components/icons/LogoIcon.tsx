
import React from 'react';

interface IconProps {
  className?: string;
}

export const LogoIcon: React.FC<IconProps> = ({ className }) => (
  <svg
    className={className}
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <defs>
      <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style={{ stopColor: 'rgb(34 211 238)', stopOpacity: 1 }} />
        <stop offset="100%" style={{ stopColor: 'rgb(217 70 239)', stopOpacity: 1 }} />
      </linearGradient>
    </defs>
    <path
      d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z"
      fill="url(#grad1)"
    />
    <circle cx="12" cy="12" r="3" fill="url(#grad1)" />
  </svg>
);