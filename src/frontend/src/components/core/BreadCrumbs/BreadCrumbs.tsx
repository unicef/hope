import * as React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import ChevronRightRoundedIcon from '@mui/icons-material/ChevronRightRounded';
import { Box } from '@mui/material';

const BreadCrumbsLink = styled(Link)`
  color: rgba(0, 0, 0, 0.87);
  font-size: 16px;
  line-height: 32px;
  text-decoration: none;
`;

const BreadCrumbsItemNotLink = styled(Box)`
  color: rgba(0, 0, 0, 0.87);
  font-size: 16px;
  line-height: 32px;
  text-decoration: none;
  cursor: pointer;
`;
const BreadCrumbsElementContainer = styled.span`
  display: flex;
  align-items: center;
`;
const Container = styled.div`
  display: flex;
  flex-direction: row;
`;
interface BreadCrumbsElementProps {
  title: string;
  to?: string;
  last: boolean;
  onClick?: () => void;
}

function BreadCrumbsElement({
  title,
  to,
  last = false,
  onClick = () => null,
}: BreadCrumbsElementProps): React.ReactElement {
  return (
    <BreadCrumbsElementContainer data-cy="breadcrumbs-element-container">
      {to ? (
        <BreadCrumbsLink to={to} data-cy="breadcrumbs-link">
          {title}
        </BreadCrumbsLink>
      ) : (
        <BreadCrumbsItemNotLink
          onClick={onClick}
          data-cy="breadcrumbs-item-not-link"
        >
          {title}
        </BreadCrumbsItemNotLink>
      )}
      {!last ? (
        <ChevronRightRoundedIcon data-cy="breadcrumbs-chevron-icon" />
      ) : null}
    </BreadCrumbsElementContainer>
  );
}
export interface BreadCrumbsItem {
  title: string;
  to?: string;
  handleClick?: () => void;
}

interface BreadCrumbsProps {
  breadCrumbs: BreadCrumbsItem[];
}

export function BreadCrumbs({
  breadCrumbs,
}: BreadCrumbsProps): React.ReactElement {
  const breadCrumbsElements = breadCrumbs.map((item, index) => {
    const last = index === breadCrumbs.length - 1;
    return (
      <BreadCrumbsElement
        key={item.title}
        title={item.title}
        to={item.to}
        onClick={item.handleClick}
        last={last}
        data-cy={`breadcrumbs-element-${index}`}
      />
    );
  });
  return (
    <Container data-cy="breadcrumbs-container">{breadCrumbsElements}</Container>
  );
}
