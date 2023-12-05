import { Box, Button } from '@material-ui/core';
import { Refresh } from '@material-ui/icons';
import DashboardIcon from '@material-ui/icons/Dashboard';
import React from 'react';
import { Link, useHistory } from 'react-router-dom';
import styled from 'styled-components';
import PageNotFoundGraphic from './404_graphic.png';
import HopeLogo from './404_hope_logo.png';

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

export const PageNotFound: React.FC = () => {
  const goBack = (): void => {
    window.history.back();
  };

  const history = useHistory();
  const pathSegments = history.location.pathname.split('/');
  const businessArea = pathSegments[2];

  return (
    <Container>
      <LogoContainer>
        <img src={HopeLogo} alt='Hope Logo' width='186' height='101' />
      </LogoContainer>
      <SquareLogo>
        <img
          src={PageNotFoundGraphic}
          alt='Brush with paint 404'
          width='354'
          height='293'
        />
      </SquareLogo>
      <TextContainer>
        <Title>Oops! Page Not Found</Title>
        <Paragraph>
          Looks like you&apos;ve ventured off the map. Don&apos;t worry, we can
          help you get back on track. Please try again or explore our other
          exciting content.
        </Paragraph>
      </TextContainer>
      <Box display='flex' justifyContent='center' alignItems='center'>
        <Box mr={4}>
          <Button
            endIcon={<Refresh />}
            variant='outlined'
            color='primary'
            onClick={goBack}
          >
            REFRESH PAGE
          </Button>
        </Box>
        <Button
          endIcon={<DashboardIcon />}
          color='primary'
          variant='contained'
          component={Link}
          to={`/${businessArea}/programs/all/list`}
        >
          GO TO PROGRAMME MANAGEMENT
        </Button>
      </Box>
    </Container>
  );
};
