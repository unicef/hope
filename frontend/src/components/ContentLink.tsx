import React from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../theme';

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
  target,
  rel,
}: {
  href: string;
  children: string;
  target?: string;
  rel?: string;
}): React.ReactElement => {
  return (
    <Link target={target} rel={rel} href={href}>
      {children}
    </Link>
  );
};
