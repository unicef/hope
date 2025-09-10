import React, {
  ReactElement,
  ButtonHTMLAttributes,
  AnchorHTMLAttributes,
} from 'react';
import styled from 'styled-components';
import { Link, LinkProps } from 'react-router-dom';

interface StyledLinkProps {
  fullWidth?: boolean;
  newTab?: boolean;
}

const StyledLink = styled(Link)<StyledLinkProps>`
  color: #000;
  max-width: ${(props) => (props.fullWidth ? '100%' : '200px')};
  overflow-wrap: break-word;
`;

const StyledLinkA = styled.a<StyledLinkProps>`
  color: #000;
  max-width: ${(props) => (props.fullWidth ? '100%' : '200px')};
  overflow-wrap: break-word;
`;

const StyledButton = styled.button<StyledLinkProps>`
  color: #000;
  background: none;
  border: none;
  padding: 0;
  margin: 0;
  cursor: pointer;
  max-width: ${(props) => (props.fullWidth ? '100%' : '200px')};
  overflow-wrap: break-word;
  text-decoration: underline;
  font: inherit;
`;

interface BlackLinkButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    StyledLinkProps {
  button: true;
  children: React.ReactNode;
}

interface BlackLinkAnchorProps
  extends AnchorHTMLAttributes<HTMLAnchorElement>,
    StyledLinkProps {
  button?: false;
  newTab?: boolean;
  to?: string;
  children: React.ReactNode;
}

interface BlackLinkRouterProps extends LinkProps, StyledLinkProps {
  button?: false;
  newTab?: false;
  to: string;
  children: React.ReactNode;
}

type BlackLinkProps =
  | BlackLinkButtonProps
  | BlackLinkAnchorProps
  | BlackLinkRouterProps;

export const BlackLink = (props: BlackLinkProps): ReactElement => {
  if ('button' in props && props.button) {
    // Button variant for modal opening
    const { children, ...rest } = props;
    return <StyledButton {...rest}>{children}</StyledButton>;
  }
  if ('newTab' in props && props.newTab) {
    // Anchor variant for external links
    const { children, to = '/', ...rest } = props as BlackLinkAnchorProps;
    // Only pass anchor props
    const anchorProps: AnchorHTMLAttributes<HTMLAnchorElement> = {};
    Object.keys(rest).forEach((key) => {
      // Only allow anchor props
      if (
        [
          'href',
          'target',
          'rel',
          'onClick',
          'style',
          'className',
          'id',
          'title',
          'tabIndex',
          'aria-label',
          'aria-labelledby',
          'aria-describedby',
          'aria-current',
          'download',
          'ref',
          'fullWidth',
        ].includes(key)
      ) {
        // @ts-ignore
        anchorProps[key] = rest[key];
      }
    });
    return (
      <StyledLinkA
        {...anchorProps}
        href={to}
        target="_blank"
        rel="noopener noreferrer"
        onClick={(e: React.MouseEvent<HTMLAnchorElement>) => {
          if (rest.onClick) rest.onClick(e);
          e.stopPropagation();
        }}
      >
        {children}
      </StyledLinkA>
    );
  }
  // Default router link
  const { children, to = '/', ...rest } = props as BlackLinkRouterProps;
  // Only pass link props
  const linkProps: Partial<LinkProps> = {};
  Object.keys(rest).forEach((key) => {
    if (
      [
        'replace',
        'state',
        'to',
        'onClick',
        'style',
        'className',
        'id',
        'title',
        'tabIndex',
        'aria-label',
        'aria-labelledby',
        'aria-describedby',
        'aria-current',
        'ref',
        'fullWidth',
      ].includes(key)
    ) {
      // @ts-ignore
      linkProps[key] = rest[key];
    }
  });
  return (
    <StyledLink
      {...linkProps}
      to={to}
      onClick={(e: React.MouseEvent<HTMLAnchorElement>) => {
        if (rest.onClick) rest.onClick(e);
        e.stopPropagation();
      }}
    >
      {children}
    </StyledLink>
  );
};
