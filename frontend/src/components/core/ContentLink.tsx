import React from 'react';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';

const Link = styled.a`
  font-family: ${({ theme }: { theme: MiśTheme }) => theme.hctTypography.fontFamily};
  color: #000;
  font-size: 14px;
  line-height: 19px;
  max-width: ${(props) => (props.fullWidth ? '100%' : '200px')}
  overflow-wrap: break-word;
`;

export function ContentLink({
  href,
  children,
  download = false,
  fullWidth = false,
}: {
  href: string;
  children: string;
  download?: boolean;
  fullWidth?: boolean;
}): React.ReactElement {
  return (
    <Link download={download} href={href} fullWidth={fullWidth}>
      {children}
    </Link>
  );
}
