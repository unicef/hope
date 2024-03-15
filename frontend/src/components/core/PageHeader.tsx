import { Box, Typography } from '@mui/material';
import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded';
import * as React from 'react';
import { styled } from '@mui/system';
import { BreadCrumbs, BreadCrumbsItem } from './BreadCrumbs';

const Wrapper = styled('div')({
  boxShadow:
    '0px 2px 4px -1px rgba(0, 0, 0, 0.2), 0px 4px 5px 0px rgba(0, 0, 0, 0.14), 0px 1px 10px 0px rgba(0, 0, 0, 0.12)',
  position: 'relative',
  width: '100%',
  backgroundColor: '#fff',
});

const Container = styled('div')({
  display: 'flex',
  alignItems: 'center',
  padding: '28px 44px',
});

const HeaderContainer = styled('div')({
  flex: 1,
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginLeft: '20px',
});

const ActionsContainer = styled('div')({
  display: 'flex',
  alignItems: 'center',
});

const BackButton = styled('div')({
  cursor: 'pointer',
});

const TabsWrapper = styled('div')({
  margin: '0 0 0 20px',
});

const TitleWrapper = styled('div')({
  width: '60%',
  minWidth: '600px',
  transform: 'translateY(-12px)',
  '& label:first-child': {
    fontSize: '24px',
  },
  '& input:first-child': {
    fontSize: '24px',
  },
  '& div:first-child': {
    margin: 0,
  },
});

const TitleContainer = styled('div')({
  width: '100%',
  wordWrap: 'break-word',
  wordBreak: 'break-all',
});

interface Props {
  title: string | React.ReactElement;
  children?: React.ReactElement;
  breadCrumbs?: BreadCrumbsItem[];
  tabs?: React.ReactElement;
  hasInputComponent?: boolean;
  flags?: React.ReactElement;
  handleBack?: () => void;
}

export function PageHeader({
  title,
  children,
  breadCrumbs = null,
  tabs = null,
  hasInputComponent,
  flags,
  handleBack,
}: Props): React.ReactElement {
  return (
    <Wrapper data-cy="page-header-container">
      <Container>
        {breadCrumbs && breadCrumbs.length !== 0 ? (
          // Leaving breadcrumbs for permissions, but BackButton goes back to the previous page
          <BackButton
            onClick={() => (handleBack ? handleBack() : window.history.back())}
          >
            <ArrowBackRoundedIcon fontSize="large" />
          </BackButton>
        ) : null}
        <HeaderContainer>
          <div>
            {React.isValidElement(title) && hasInputComponent ? (
              <TitleWrapper data-cy="page-header-title">{title}</TitleWrapper>
            ) : (
              <>
                {breadCrumbs && <BreadCrumbs breadCrumbs={breadCrumbs} />}
                <Box display="flex" alignItems="center">
                  <TitleContainer>
                    <Typography data-cy="page-header-title" variant="h5">
                      {title}
                    </Typography>
                  </TitleContainer>
                  <Box display="flex" ml={2}>
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
}
