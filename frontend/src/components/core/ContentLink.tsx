import React from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';

const Link = styled.a`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 14px;
  line-height: 19px;
`;

export const ContentLink = ({
  href,
  children,
  download = false,
}: {
  href: string;
  children: string;
  download?: boolean;
}): React.ReactElement => {
  return (
    <Link download={download} href={href}>
      {children}
    </Link>
  );
};
