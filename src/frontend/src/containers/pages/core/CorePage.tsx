import { Typography } from '@mui/material';
import type { ReactElement } from 'react';
import styled from 'styled-components';
import { Logo } from '@components/core/Logo';

const photoModules = import.meta.glob<string>(
  '../../../backgrounds/*.{jpg,jpeg,png}',
  { eager: true, import: 'default' },
);

export const CORE_PATH = String.fromCharCode(106, 97, 110);

const photos = Object.keys(photoModules)
  .sort()
  .map((path) => photoModules[path]);

const Container = styled.div`
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #00adef;
  box-sizing: border-box;
  padding: 24px 16px;
`;

const Heading = styled(Typography)`
  && {
    color: #fff;
    font-size: 36px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-align: center;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    column-gap: 4px;
  }
`;

// Two 4:3 rows must fit the viewport height together with the heading.
const Gallery = styled.div`
  width: 100%;
  max-width: calc((100vh - 190px) * 4 / 3 + 16px);
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;

  @media (max-width: 700px) {
    max-width: none;
    grid-template-columns: 1fr;
  }
`;

const Photo = styled.img`
  width: 100%;
  max-width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  display: block;
`;

export function CorePage(): ReactElement {
  return (
    <Container>
      <Heading>
        <span>Thank you for all the memories and</span>
        <Logo transparent={false} displayLogoWithoutSubtitle height={90} />
      </Heading>
      {photos.length > 0 && (
        <Gallery>
          {photos.map((src, index) => (
            <Photo key={src} src={src} alt={`Memory ${index + 1}`} />
          ))}
        </Gallery>
      )}
    </Container>
  );
}
