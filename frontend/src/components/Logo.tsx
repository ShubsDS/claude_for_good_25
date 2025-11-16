interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
}

export default function Logo({ size = 'md', showText = true, className = '' }: LogoProps) {
  const sizes = {
    sm: { icon: 'h-8 w-8', text: 'text-2xl' },
    md: { icon: 'h-12 w-12', text: 'text-3xl' },
    lg: { icon: 'h-16 w-16', text: 'text-4xl' },
    xl: { icon: 'h-24 w-24', text: 'text-6xl' },
  };

  const currentSize = sizes[size];

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* Logo Icon - Stylized "S" with graduation cap theme */}
      <div className={`${currentSize.icon} relative`}>
        <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          {/* Graduation cap top */}
          <path
            d="M50 15L85 30L50 45L15 30L50 15Z"
            fill="url(#gradient1)"
            stroke="#1e40af"
            strokeWidth="2"
          />
          {/* Stylized "S" shape integrated with cap */}
          <path
            d="M65 50C65 42 58 38 50 38C42 38 35 42 35 50C35 58 42 62 50 62C58 62 65 66 65 74C65 82 58 86 50 86C42 86 35 82 35 74"
            stroke="url(#gradient2)"
            strokeWidth="6"
            strokeLinecap="round"
            fill="none"
          />
          {/* Tassel */}
          <circle cx="85" cy="30" r="4" fill="#dc2626" />
          <line x1="85" y1="34" x2="85" y2="42" stroke="#dc2626" strokeWidth="2" />

          <defs>
            <linearGradient id="gradient1" x1="15" y1="15" x2="85" y2="45">
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#1e40af" />
            </linearGradient>
            <linearGradient id="gradient2" x1="35" y1="38" x2="65" y2="86">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="100%" stopColor="#4f46e5" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Logo Text */}
      {showText && (
        <div className={`font-bold ${currentSize.text} bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent`}>
          Scorra
        </div>
      )}
    </div>
  );
}
