import styled from 'styled-components';
import logoWithoutSubtitleTransparent from '../../images/logo-transparent1.png';
import logoWithSubtitleTransparent from '../../images/logo-with-subtitle-transparent1.png';
import logoWithoutSubtitle from '../../images/logo1.jpg';
import logoWithSubtitle from '../../images/logo-with-subtitle1.jpg';
import { ReactElement } from 'react';

const Image = styled.img`
  height: ${(props) => `${props.height}px`};
`;

interface LogoProps {
  transparent: boolean;
  displayLogoWithoutSubtitle: boolean;
  height?: number;
}

export function Logo({
  transparent,
  displayLogoWithoutSubtitle,
  height,
}: LogoProps): ReactElement {
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

  const imageHeight = displayLogoWithoutSubtitle === true ? 64 : 206;

  return (
    <Image
      height={height || imageHeight}
      src={logoSrc}
      alt="HOPE Portal Logo"
    />
  );
}
