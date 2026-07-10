import { Typography } from '@mui/material';
import { ReactElement, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { Logo } from '@components/core/Logo';
import surpriseFallback from '../../../images/surprise-fallback.jpg';

const Container = styled.div`
  width: 100vw;
  height: 100vh;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  display: flex;
  background-color: #003c8f;
`;

const Card = styled.div`
  text-align: center;
  width: 100%;
  padding: 40px 0;
`;

const Heading = styled(Typography)`
  && {
    color: #fff;
    font-size: 28px;
    font-weight: 700;
    margin-top: 24px;
    letter-spacing: 0.5px;
    padding: 0 16px;
  }
`;

const SubHeading = styled(Typography)`
  && {
    color: #fff;
    font-size: 16px;
    font-weight: 300;
    margin-top: 8px;
    margin-bottom: 24px;
    opacity: 0.9;
    padding: 0 16px;
  }
`;

const Photo = styled.img`
  width: 100vw;
  max-height: 70vh;
  object-fit: contain;
  display: block;
`;

const BackLink = styled(Link)`
  display: inline-block;
  margin-top: 28px;
  color: #fff;
  font-size: 14px;
  text-decoration: underline;
  opacity: 0.85;

  &:hover {
    opacity: 1;
  }
`;

const DEFAULT_HEADING = '🎉 You found a secret!';
const DEFAULT_SUBHEADING = 'Congratulations, explorer.';

export function SurprisePage(): ReactElement {
  const [imageSrc, setImageSrc] = useState<string>(surpriseFallback);
  const [heading, setHeading] = useState<string>(DEFAULT_HEADING);
  const [subheading, setSubheading] = useState<string>(DEFAULT_SUBHEADING);

  useEffect(() => {
    fetch('/api/rest/surprise/')
      .then((res) => res.json())
      .then((data: { image: string | null; heading: string; subheading: string }) => {
        if (data.image) setImageSrc(data.image);
        if (data.heading) setHeading(data.heading);
        if (data.subheading) setSubheading(data.subheading);
      })
      .catch(() => {
        // keep defaults
      });
  }, []);

  return (
    <Container>
      <Card>
        <Logo transparent={false} displayLogoWithoutSubtitle={false} height={160} />
        <Heading>{heading}</Heading>
        <SubHeading>{subheading}</SubHeading>
        <Photo src={imageSrc} alt="A surprise for you" />
        <BackLink to="/login">← Back to login</BackLink>
      </Card>
    </Container>
  );
}
