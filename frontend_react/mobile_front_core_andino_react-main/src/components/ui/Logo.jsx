export default function Logo({
  size = 44,
  wordmark = true,
  variant = 'dark',
  subtitle = 'CORE FINANCIERO',
}) {
  const textColor = variant === 'light' ? '#ffffff' : '#4F2D7F';
  const subColor = variant === 'light' ? 'rgba(255,255,255,.85)' : '#6b6b7b';
  const nameSize = Math.round(size * 0.5);
  const subSize = Math.max(9, Math.round(size * 0.23));

  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 12 }}>
      {/* Logo con imagen - USA TU LOGO DESCARGADO */}
      <img
        src="/logo_ripley.png"
        alt="Banco Ripley"
        style={{
          width: size,
          height: size,
          objectFit: 'contain',
        }}
      />

      {wordmark && (
        <span style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.04 }}>
          <span style={{ fontWeight: 800, fontSize: nameSize, color: textColor, letterSpacing: '-0.5px' }}>
            Banco Ripley
          </span>
          {subtitle && (
            <span style={{ fontSize: subSize, fontWeight: 700, color: subColor, letterSpacing: '1.2px' }}>
              {subtitle}
            </span>
          )}
        </span>
      )}
    </span>
  );
}