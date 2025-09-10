import styled from 'styled-components';
import MaintenanceGraphic from './maintenance_graphic_painter.png';
import HopeLogo from './maintenance_hope_logo.png';
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

const Button = styled.button`
  background-color: transparent;
  border: 2px solid #033f91;
  border-radius: 4px;
  padding: 6px 16px;
  font-size: 14px;
  font-weight: 600;
  line-height: 16px;
  letter-spacing: 1.25px;
  color: #033f91;
  cursor: pointer;
`;

const Icon = styled.img`
  vertical-align: middle;
  margin-left: 5px;
  width: 28px;
  height: 28px;
`;

export const MaintenancePage: FC = () => {
  const goBackAndClearCache = () => {
    window.history.back();
  };
  return (
    <Container>
      <LogoContainer>
        <img src={HopeLogo} alt="Hope Logo" width="186" height="101" />
      </LogoContainer>

      <SquareLogo>
        <img
          src={MaintenanceGraphic}
          alt="Brush with paint"
          width="354"
          height="293"
        />
      </SquareLogo>

      <TextContainer>
        <Title>System under maintenance</Title>
        <Paragraph>
          Sorry for the inconvenience. Maintenance is underway to enhance our
          services. System will be back shortly!
        </Paragraph>
      </TextContainer>

      <Button onClick={goBackAndClearCache}>
        REFRESH PAGE
        <Icon
          src="./refresh_icon.png"
          alt="Refresh Icon"
          width="20"
          height="20"
        />
      </Button>
    </Container>
  );
};
