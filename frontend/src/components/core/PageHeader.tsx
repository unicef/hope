import { Box, Typography } from '@material-ui/core';
import ArrowBackRoundedIcon from '@material-ui/icons/ArrowBackRounded';
import React from 'react';
import styled from 'styled-components';
import { registrationDataImportErasedColor } from '../../utils/utils';
import { BreadCrumbs, BreadCrumbsItem } from './BreadCrumbs';
import { StatusBox } from './StatusBox';

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
  align-items: center;
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
`;

const TitleWrapper = styled.div`
  width: 60%;
  min-width: 600px;
  transform: translateY(-12px);
  label:first-child {
    font-size: ${({ theme }) => theme.spacing(6)}px;
  }
  input:first-child {
    font-size: ${({ theme }) => theme.spacing(6)}px;
  }
  div:first-child {
    margin: 0;
  }
`;

const StatusErasedWrapper = styled.div`
  margin-left: 15px;
  text-transform: uppercase;
`;

const TitleContainer = styled.div`
  width: 100%;
  word-wrap: break-word;
  word-break: break-all;
`;
interface Props {
  title: string | React.ReactElement;
  children?: React.ReactElement;
  breadCrumbs?: BreadCrumbsItem[];
  tabs?: React.ReactElement;
  hasInputComponent?: boolean;
  flags?: React.ReactElement;
  handleBack?: () => void;
}

export const PageHeader = ({
  title,
  children,
  breadCrumbs = null,
  tabs = null,
  hasInputComponent,
  flags,
  handleBack,
}: Props): React.ReactElement => {
  return (
    <Wrapper data-cy='page-header-container'>
      <Container>
        {breadCrumbs && breadCrumbs.length !== 0 ? (
          // Leaving breadcrumbs for permissions, but BackButton goes back to the previous page
          <BackButton
            onClick={() => (handleBack ? handleBack() : window.history.back())}
          >
            <ArrowBackRoundedIcon fontSize='large' />
          </BackButton>
        ) : null}
        <HeaderContainer>
          <div>
            {React.isValidElement(title) && hasInputComponent ? (
              <TitleWrapper data-cy='page-header-title'>{title}</TitleWrapper>
            ) : (
              <>
                {breadCrumbs && <BreadCrumbs breadCrumbs={breadCrumbs} />}
                <Box display='flex' alignItems='center'>
                  <TitleContainer>
                    <Typography data-cy='page-header-title' variant='h5'>
                      {title}
                    </Typography>
                  </TitleContainer>
                  <Box display='flex' ml={2}>
                    {flags}
                  </Box>
                </Box>
              </>
            )}
          </div>
          <ActionsContainer>{children || null}</ActionsContainer>
        </HeaderContainer>
      </Container>
      <TabsWrapper>{tabs}</TabsWrapper>
    </Wrapper>
  );
};
