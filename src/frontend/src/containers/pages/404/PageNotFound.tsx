import { Box, Button } from '@mui/material';
import { Refresh } from '@mui/icons-material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { responsiveValue } from 'src/responsive';
import PageNotFoundGraphic from './404_graphic.png';
import HopeLogo from './404_hope_logo.png';
import type { FC } from 'react';

const Container = styled(Box)`
  background-color: #ffffff;
  text-align: center;
  font-family: 'Roboto', sans-serif;
  height: 100vh;
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
  font-size: 24px;
  color: #666666;
  line-height: 32px;
`;

export const PageNotFound: FC = () => {
  const navigate = useNavigate();

  const goBackAndClearCache = () => {
    navigate(-1);
  };

  return (
    <Container
      sx={{
        pt: responsiveValue('16px', '150px'),
        px: responsiveValue('16px', '0'),
      }}
    >
      <LogoContainer sx={{ position: responsiveValue('static', 'absolute') }}>
        <img src={HopeLogo} alt="Hope Logo" width="186" height="101" />
      </LogoContainer>
      <SquareLogo
        sx={{
          maxWidth: '100%',
          boxSizing: 'border-box',
          '& img': {
            maxWidth: '100%',
            height: responsiveValue('auto', '293px'),
          },
        }}
      >
        <img
          src={PageNotFoundGraphic}
          alt="Brush with paint 404"
          width="354"
          height="293"
        />
      </SquareLogo>
      <TextContainer>
        <Title data-cy="page-not-found-title">Oops! Page Not Found</Title>
        <Paragraph>
          Looks like you&apos;ve ventured off the map. Don&apos;t worry, we can
          help you get back on track. Please try again or explore our other
          exciting content.
        </Paragraph>
      </TextContainer>
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: responsiveValue(2, 0),
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <Box
          sx={{
            mr: responsiveValue(0, 4),
          }}
        >
          <Button
            endIcon={<Refresh />}
            variant="outlined"
            color="primary"
            onClick={() => {
              goBackAndClearCache();
            }}
            data-cy="button-refresh-page"
          >
            REFRESH PAGE
          </Button>
        </Box>
        <Button
          endIcon={<DashboardIcon />}
          color="primary"
          variant="contained"
          component={Link}
          data-cy="go-to-programme-management"
          to="/"
        >
          GO TO PROGRAMME MANAGEMENT
        </Button>
      </Box>
    </Container>
  );
};
