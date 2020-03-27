import React from 'react';
import { Typography } from '@material-ui/core';
import styled from 'styled-components';
import { useHistory } from 'react-router-dom';
import ArrowBackRoundedIcon from '@material-ui/icons/ArrowBackRounded';
import { BreadCrumbs, BreadCrumbsItem } from './BreadCrumbs';

const Wrapper = styled.div`
  box-shadow: 0px 2px 4px -1px rgba(0, 0, 0, 0.2),
    0px 4px 5px 0px rgba(0, 0, 0, 0.14), 0px 1px 10px 0px rgba(0, 0, 0, 0.12);
  position: relative;
  width: 100%;
  background-color: #fff;
`;

const Container = styled.div`
  display: flex;
  align-items: center;
  padding: ${({ theme }) => theme.spacing(7)}px
    ${({ theme }) => theme.spacing(11)}px;
`;
const HeaderContainer = styled.div`
  flex: 1;
  display: flex;
  justify-content: space-between;
  margin-left: ${({ theme }) => theme.spacing(5)}px;
`;
const ActionsContainer = styled.div`
  display: flex;
  align-items: center;
`;
const BackButton = styled.div`
  cursor: pointer;
`;

const TabsWrapper = styled.div`
  margin: 0 0 0 ${({ theme }) => theme.spacing(5)}px;
`

interface Props {
  title: string | React.ReactElement;
  children?: React.ReactElement;
  breadCrumbs?: BreadCrumbsItem[];
  tabs?: React.ReactElement;
}

export function PageHeader({
  title,
  children,
  breadCrumbs = null,
  tabs = null,
}: Props): React.ReactElement {
  const history = useHistory();
  return (
    <Wrapper>
      <Container>
        {breadCrumbs && breadCrumbs.length !== 0 ? (
          <BackButton
            onClick={() => history.push(breadCrumbs[breadCrumbs.length - 1].to)}
          >
            <ArrowBackRoundedIcon fontSize='large' />
          </BackButton>
        ) : null}
        <HeaderContainer>
          <div>
            <div>
              {breadCrumbs && <BreadCrumbs breadCrumbs={breadCrumbs} />}
              <Typography variant='h5'>{title}</Typography>
            </div>
          </div>
          <ActionsContainer>{children || null}</ActionsContainer>
        </HeaderContainer>
      </Container>
      <TabsWrapper>{tabs}</TabsWrapper>
    </Wrapper>
  );
}
