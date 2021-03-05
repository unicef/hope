import React from 'react';
import styled from 'styled-components';
import logoWithoutSubtitleTransparent from '../images/logo-transparent.png';
import logoWithSubtitleTransparent from '../images/logo-with-subtitle-transparent.png';
import logoWithoutSubtitle from '../images/logo.jpg';
import logoWithSubtitle from '../images/logo-with-subtitle.jpg';

const Image = styled.img`
  height: ${props => `${props.height}px`};
`;

interface LogoProps {
  transparent: boolean;
  displayLogoWithoutSubtitle: boolean;
  height?: number;
}

export const Logo = ({
  transparent,
  displayLogoWithoutSubtitle,
    height,
}: LogoProps): React.ReactElement => {
  let logoSrc;
  if (transparent) {
    logoSrc =
      displayLogoWithoutSubtitle === true
        ? logoWithoutSubtitleTransparent
        : logoWithSubtitleTransparent;
  } else {
    logoSrc =
      displayLogoWithoutSubtitle === true
        ? logoWithoutSubtitle
        : logoWithSubtitle;
  }

  const imageHeight = displayLogoWithoutSubtitle === true ? 64 : 206

  return <Image height={height || imageHeight} src={logoSrc} alt='HOPE Portal Logo' />;
};
