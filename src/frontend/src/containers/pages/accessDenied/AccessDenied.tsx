import { Box, Button } from '@mui/material';
import { Refresh } from '@mui/icons-material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import styled from 'styled-components';
import AccessDeniedGraphic from './access_denied.png';
import HopeLogo from './access_denied_hope_logo.png';
import { FC } from 'react';

const Container = styled.div`
  background-color: #ffffff;
  text-align: center;
  padding-top: 150px;
  font-family: 'Roboto', sans-serif;
  height: 100vh;
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
  font-size: 24px;
  color: #666666;
  line-height: 32px;
`;

export const AccessDenied: FC = () => {
  const refreshAndClearCache = () => {
    window.history.back();
  };

  const handleGoBack = (): void => {
    if (window.history.length > 2) {
      window.history.go(-2);
    } else {
      window.history.back();
    }
  };

  return (
    <Container>
      <LogoContainer>
        <img src={HopeLogo} alt="Hope Logo" width="186" height="101" />
      </LogoContainer>
      <SquareLogo>
        <img
          src={AccessDeniedGraphic}
          alt="Hand denying access"
          width="354"
          height="293"
        />
      </SquareLogo>
      <TextContainer>
        <Title>Access Denied</Title>
        <Paragraph>
          Sorry, the page you&apos;re trying to reach either doesn&apos;t exist
          or you don&apos;t have the required permissions to view it.
        </Paragraph>
      </TextContainer>
      <Box display="flex" justifyContent="center" alignItems="center">
        <Box mr={4}>
          <Button
            endIcon={<Refresh />}
            variant="outlined"
            color="primary"
            onClick={refreshAndClearCache}
            data-cy="button-refresh-page"
          >
            REFRESH PAGE
          </Button>
        </Box>
        <Button
          endIcon={<ArrowBackIcon />}
          color="primary"
          variant="contained"
          onClick={handleGoBack}
          data-cy="button-go-back"
        >
          GO BACK
        </Button>
      </Box>
    </Container>
  );
};
