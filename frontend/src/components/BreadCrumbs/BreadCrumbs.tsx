import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import ChevronRightRoundedIcon from '@material-ui/icons/ChevronRightRounded';

const BreadCrumbsLink = styled(Link)`
  color: rgba(0, 0, 0, 0.87);
  font-size: 16px;
  line-height: 32px;
  text-decoration: none;
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
  to: string;
  last: boolean;
}

function BreadCrumbsElement({
  title,
  to,
  last = false,
}: BreadCrumbsElementProps): React.ReactElement {
  return (
    <BreadCrumbsElementContainer>
      <BreadCrumbsLink to={to}>{title}</BreadCrumbsLink>
      {!last ? <ChevronRightRoundedIcon /> : null}
    </BreadCrumbsElementContainer>
  );
}
export interface BreadCrumbsItem {
  title: string;
  to: string;
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
        last={last}
      />
    );
  });
  return <Container>{breadCrumbsElements}</Container>;
}
