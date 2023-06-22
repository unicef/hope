import React from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';

const Link = styled.a`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #000;
  font-size: 14px;
  line-height: 19px;
  max-width: 150px;
  text-overflow: ellipsis;
  overflow: hidden;
  white-space: nowrap;
  display: inline-block;
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
