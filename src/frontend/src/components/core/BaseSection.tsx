import { Box, Typography } from '@mui/material';
import { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { GreyText } from './GreyText';

const PaperContainer = styled(Box)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)} ${({ theme }) => theme.spacing(4)};
  flex-direction: column;
  background-color: #fff;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  width: 100%;
`;

const BoxContainer = styled(Box)`
  display: flex;
  padding: ${({ theme }) => theme.spacing(3)} ${({ theme }) => theme.spacing(4)};
  flex-direction: column;
  width: 100%;
`;

interface BaseSectionProps {
  children?: ReactElement | ReactElement[];
  buttons?: ReactElement;
  title?: string | ReactElement;
  description?: string;
  p?: number;
  noPaper?: boolean;
  tabs?: ReactElement;
  stepper?: ReactElement;
}

export const BaseSection = ({
  children = <></>,
  buttons,
  title = '',
  description,
  p = 3,
  noPaper = false,
  tabs = null,
  stepper = null,
}: BaseSectionProps): ReactElement => {
  const { t } = useTranslation();
  const Container = noPaper ? BoxContainer : PaperContainer;

  return (
    <Container>
      <Box p={p}>
        {stepper && <Box mb={2}>{stepper}</Box>}
        <Box
          p={p}
          display="flex"
          justifyContent="space-between"
          alignItems="center"
        >
          <Box>
            {typeof title === 'string' ? (
              <Typography data-cy="title" variant="h6">
                {t(title)}
              </Typography>
            ) : (
              title
            )}
          </Box>
          {buttons}
        </Box>
        {tabs && <Box mb={2}>{tabs}</Box>}
        {description && (
          <Box pl={p} mb={2}>
            <GreyText data-cy="description">{description}</GreyText>
          </Box>
        )}
        <Box>{children}</Box>
      </Box>
    </Container>
  );
};
