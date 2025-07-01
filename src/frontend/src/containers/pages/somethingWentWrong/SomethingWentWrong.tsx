import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Box, Button } from '@mui/material';
import { clearCache } from '@utils/utils';
import { useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { getClient } from '../../../apollo/client';
import SomethingWentWrongGraphic from './something_went_wrong_graphic.png';
import HopeLogo from './something_went_wrong_hope_logo.png';
import { FC } from 'react';

const Container = styled.div`
  background-color: #ffffff;
  text-align: center;
  padding-top: 30px;
  font-family: 'Roboto', sans-serif;
  height: 100vh;
  width: 100%;
`;

const LogoContainer = styled.div`
  position: absolute;
  top: 20px;
  left: 20px;
`;

const SquareLogo = styled.div`
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
}

export const SomethingWentWrong: FC<SomethingWentWrongProps> = ({
  pathname,
  errorMessage: propsErrorMessage,
  component,
}) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleGoBackAndClearCache = async (): Promise<void> => {
    const client = await getClient();
    await clearCache(client);
    if (location.state?.lastSuccessfulPage) {
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
    <Container>
      <LogoContainer>
        <img src={HopeLogo} alt="Hope Logo" width="130" height="71" />{' '}
      </LogoContainer>
      <SquareLogo>
        <img
          src={SomethingWentWrongGraphic}
          alt="Sad face"
          width="248"
          height="205"
        />
      </SquareLogo>
      <TextContainer>
        <Title>Oops! Something went wrong</Title>
        {errorMessage && isEnvWhereShowErrors ? (
          <Box display="flex" flexDirection="column">
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
            {component && <Paragraph>Component: {component}</Paragraph>}
          </Box>
        ) : (
          <Paragraph>
            Don&apos;t worry! Our team is on it, working to fix the issue.
            Please try again later. Thank you for your patience.
          </Paragraph>
        )}
      </TextContainer>
      <Box display="flex" justifyContent="center" alignItems="center">
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
