import { Box, Typography } from '@mui/material';
import ArrowBackRoundedIcon from '@mui/icons-material/ArrowBackRounded';
import { styled } from '@mui/system';
import type { BreadCrumbsItem } from './BreadCrumbs';
import { BreadCrumbs } from './BreadCrumbs';
import type { ReactElement } from 'react';
import { isValidElement } from 'react';
import { responsiveValue } from 'src/responsive';

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
});

const HeaderContainer = styled('div')({
  flex: 1,
  display: 'flex',
  justifyContent: 'space-between',
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
  title: string | ReactElement;
  children?: ReactElement;
  breadCrumbs?: BreadCrumbsItem[];
  tabs?: ReactElement;
  hasInputComponent?: boolean;
  flags?: ReactElement;
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
}: Props): ReactElement {
  return (
    <Wrapper data-cy="page-header-container">
      <Container sx={{ padding: responsiveValue('16px', '28px 44px') }}>
        {breadCrumbs && breadCrumbs.length !== 0 ? (
          // Leaving breadcrumbs for permissions, but BackButton goes back to the previous page
          <BackButton
            data-cy="arrow_back"
            onClick={() => (handleBack ? handleBack() : window.history.back())}
          >
            <ArrowBackRoundedIcon fontSize="large" />
          </BackButton>
        ) : null}
        <HeaderContainer
          sx={{
            flexDirection: responsiveValue('column', 'row'),
            alignItems: responsiveValue('flex-start', 'center'),
            gap: responsiveValue(2, 0),
            minWidth: responsiveValue('0', 'auto'),
            marginLeft: responsiveValue('8px', '20px'),
          }}
        >
          <div>
            {isValidElement(title) && hasInputComponent ? (
              <TitleWrapper
                data-cy="page-header-title"
                sx={{
                  width: responsiveValue('100%', '60%'),
                  minWidth: responsiveValue('0', '600px'),
                }}
              >
                {title}
              </TitleWrapper>
            ) : (
              <>
                {breadCrumbs && <BreadCrumbs breadCrumbs={breadCrumbs} />}
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                  }}
                >
                  <TitleContainer>
                    <Typography data-cy="page-header-title" variant="h5">
                      {title}
                    </Typography>
                  </TitleContainer>
                  <Box
                    data-cy="button-admin"
                    sx={{
                      display: 'flex',
                      ml: 2,
                    }}
                  >
                    {flags}
                  </Box>
                </Box>
              </>
            )}
          </div>
          <ActionsContainer
            sx={{
              flexWrap: responsiveValue('wrap', 'nowrap'),
              gap: responsiveValue(2, 0),
            }}
          >
            {children || null}
          </ActionsContainer>
        </HeaderContainer>
      </Container>
      <TabsWrapper>{tabs}</TabsWrapper>
    </Wrapper>
  );
}
