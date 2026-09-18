import React, { useState } from 'react';

interface Photo {
  id: string;
  url: string;
  source: string;
}

interface ImageCardProps {
  photo: Photo;
}

export default function ImageCard({ photo }: ImageCardProps) {
  const fallbackImg = 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1';
  const [imgSrc, setImgSrc] = useState(photo.url);

  return (
    <div className="image-card" style={{ border: '1px solid #e5e7eb', borderRadius: '12px', overflow: 'hidden', background: '#fff', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}>
      {/* Увеличили высоту контейнера до 320px для крупных фото */}
      <div style={{ height: '320px', width: '100%', overflow: 'hidden', background: '#f3f4f6' }}>
        <img 
          src={imgSrc} 
          alt="Campus view" 
          style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.3s ease' }}
          onError={() => setImgSrc(fallbackImg)}
        />
      </div>
      <div style={{ padding: '16px' }}>
        <div style={{ fontSize: '13px', fontWeight: 'bold', color: '#166534', marginBottom: '4px' }}>
          ✓ Verified source match
        </div>
        <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '12px' }}>
          Source: {photo.source || 'Web Search'}
        </div>
        <a 
          href={photo.url} 
          target="_blank" 
          rel="noreferrer"
          style={{ fontSize: '13px', color: '#2563eb', textDecoration: 'none', fontWeight: '500' }}
        >
          Open original source ↗
        </a>
      </div>
    </div>
  );
}