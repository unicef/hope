import React from 'react';
import styled from 'styled-components';

const ZoomPhoto = styled.div<{ $src: string }>`
  width: 64px;
  &:hover::after {
    content: '';
    background-image: url(${({ $src }) => $src});
    width: 450px;
    height: 450px;
    background-size: 450px 450px;
    position: absolute;
    z-index: 2;
    top: 0;
    right: 120px;
  }
`;

const ZoomContainer = styled.div`
  position: relative;
`;

interface PhotoPreviewProps {
  children: React.ReactNode;
  src: string | string[];
}

export const PhotoPreview = ({
  children,
  src,
}: PhotoPreviewProps): React.ReactElement => (
  <ZoomContainer>
    <ZoomPhoto $src={src}>{children}</ZoomPhoto>
  </ZoomContainer>
);
