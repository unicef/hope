import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Box, Button } from '@mui/material';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { responsiveValue } from 'src/responsive';
import SomethingWentWrongGraphic from './something_went_wrong_graphic.png';
import HopeLogo from './something_went_wrong_hope_logo.png';
import type { FC } from 'react';

const Container = styled(Box)`
  background-color: #ffffff;
  text-align: center;
  font-family: 'Roboto', sans-serif;
  height: 100vh;
  width: 100%;
`;

const LogoContainer = styled(Box)`
  top: 20px;
  left: 20px;
`;

const SquareLogo = styled(Box)`
  display: inline-block;
  background-color: white;
  padding: 20px;
  margin-bottom: 20px;
`;

const TextContainer = styled.div`
  max-width: 450px;
  text-align: center;
  margin: 0 auto;
`;

const Title = styled.h1`
  font-size: 32px;
  font-weight: lighter;
  color: #233944;
  line-height: 32px;
`;

const Paragraph = styled.p`
  font-size: 18px;
  color: #666666;
  line-height: 32px;
`;

interface SomethingWentWrongProps {
  pathname?: string;
  errorMessage?: string;
  component?: string;
  goBackAddress?: string;
  specificError?: string;
}

export const SomethingWentWrong: FC<SomethingWentWrongProps> = ({
  pathname,
  errorMessage: propsErrorMessage,
  component,
  goBackAddress,
  specificError,
}) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleGoBackAndClearCache = () => {
    if (goBackAddress) {
      navigate(goBackAddress);
    } else if (location.state?.lastSuccessfulPage) {
      navigate(location.state.lastSuccessfulPage);
    } else {
      window.history.back();
    }
  };

  const isEnvWhereShowErrors =
    window.location.hostname.includes('localhost') ||
    window.location.href.includes('dev') ||
    window.location.href.includes('trn') ||
    window.location.href.includes('stg');

  const errorMessage = location.state?.errorMessage || propsErrorMessage;

  return (
    <Container
      sx={{
        pt: responsiveValue('16px', '30px'),
        px: responsiveValue('16px', '0'),
      }}
    >
      <LogoContainer sx={{ position: responsiveValue('static', 'absolute') }}>
        <img src={HopeLogo} alt="Hope Logo" width="130" height="71" />{' '}
      </LogoContainer>
      <SquareLogo
        sx={{
          maxWidth: '100%',
          boxSizing: 'border-box',
          '& img': {
            maxWidth: '100%',
            height: responsiveValue('auto', '205px'),
          },
        }}
      >
        <img
          src={SomethingWentWrongGraphic}
          alt="Sad face"
          width="248"
          height="205"
        />
      </SquareLogo>
      <TextContainer>
        <Title>Oops! Something went wrong</Title>
        {specificError ? (
          <Paragraph>Error: {specificError}</Paragraph>
        ) : isEnvWhereShowErrors && errorMessage ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {pathname && (
              <Paragraph style={{ wordWrap: 'break-word' }}>
                Location: {pathname}
              </Paragraph>
            )}
            {errorMessage && (
              <Paragraph style={{ wordWrap: 'break-word' }}>
                Error: {errorMessage}
              </Paragraph>
            )}
            {component && (
              <Paragraph style={{ wordWrap: 'break-word' }}>
                Component: {component}
              </Paragraph>
            )}
          </Box>
        ) : (
          <Paragraph>
            Don&apos;t worry! Our team is on it, working to fix the issue.
            Please try again later. Thank you for your patience.
          </Paragraph>
        )}
      </TextContainer>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Button
          endIcon={<ArrowBackIcon />}
          color="primary"
          variant="contained"
          onClick={handleGoBackAndClearCache}
          data-cy="button-go-back"
        >
          GO BACK
        </Button>
      </Box>
    </Container>
  );
};
