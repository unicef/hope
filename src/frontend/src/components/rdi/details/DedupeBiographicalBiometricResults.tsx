import { DialogDescription } from '@containers/dialogs/DialogDescription';
import { DialogFooter } from '@containers/dialogs/DialogFooter';
import { DialogTitleWrapper } from '@containers/dialogs/DialogTitleWrapper';
import { BlackLink } from '@core/BlackLink';
import {
  DeduplicationEngineSimilarityPairIndividualNode,
  DeduplicationResultNode,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { MiśTheme } from '../../../theme';
import BiometricsResultsRdi from './BiometricsResultsRdi';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

const Error = styled.span`
  color: ${({ theme }: { theme: MiśTheme }) => theme.hctPalette.red};
  font-weight: bold;
  text-decoration: underline;
  cursor: pointer;
`;
const Bold = styled.span`
  font-weight: bold;
  font-size: 16px;
`;

const StyledTable = styled(Table)`
  min-width: 100;
`;

interface DedupeBiographicalBiometricResultsProps {
  individual: IndividualDetail;
  status: string;
  results: Array<DeduplicationResultNode>;
  biometricResults: Array<DeduplicationEngineSimilarityPairIndividualNode>;
  isInBatch?: boolean;
}

export function DedupeBiographicalBiometricResults({
  individual,
  status,
  results,
  biometricResults,
  isInBatch = false,
}: DedupeBiographicalBiometricResultsProps): ReactElement {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { baseUrl } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  const createBiographicalData = (
    unicefId: string,
    fullName: string,
    age: number,
    location: string | undefined,
    score: number | undefined,
    proximityToScore: number | undefined,
    hitId: string,
  ) => {
    return {
      unicefId,
      fullName,
      age,
      location: location || 'N/A',
      score: score || 0,
      proximityToScore: proximityToScore || 0,
      hitId,
    };
  };

  const createBiometricData = (
    unicefId: string,
    fullName: string,
    age: number,
    location: string | undefined,
    similarityScore: number | undefined,
    id: string,
  ) => {
    return {
      unicefId,
      fullName,
      age,
      location: location || 'N/A',
      similarityScore: similarityScore || 0,
      id,
    };
  };

  const rows = results.map((result) => {
    return createBiographicalData(
      result.unicefId,
      result.fullName,
      result.age,
      result.location,
      result.score,
      result.proximityToScore,
      result.hitId,
    );
  });

  const biometricRows = biometricResults.map((result) => {
    return createBiometricData(
      result.unicefId,
      result.fullName,
      result.age,
      result.location,
      result.similarityScore,
      result.id,
    );
  });
  const getIndividualDetailsPath = (id): string => {
    const path = `/${baseUrl}/population/individuals/${id}`;
    return path;
  };

  const biographicalRows = rows.sort((a, b) => b.score - a.score);
  const biometricSortedRows = biometricRows.sort(
    (a, b) => b.similarityScore - a.similarityScore,
  );

  return (
    <>
      <Error
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setOpen(true);
        }}
      >
        {status} ({results.length + biometricResults.length})
      </Error>
      <Dialog
        maxWidth="md"
        fullWidth
        open={open}
        onClose={() => setOpen(false)}
        scroll="paper"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitleWrapper>
          <DialogTitle>{t('Duplicates')}</DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <DialogDescription>
            <div>
              {t('Duplicates of')}{' '}
              <Bold>
                {individual.fullName} ({individual.unicefId})
              </Bold>{' '}
              {isInBatch ? t('within batch ') : t('against population ')}
              {t('are listed below.')}
            </div>
          </DialogDescription>
          <div>
            <h3>{t('Biographical')}</h3>
            <StyledTable>
              <TableHead>
                <TableRow>
                  <TableCell style={{ width: 100 }}>
                    {t(`${beneficiaryGroup?.memberLabel} ID`)}
                  </TableCell>
                  <TableCell style={{ width: 100 }}>{t('Full Name')}</TableCell>
                  <TableCell style={{ width: 100 }}>{t('Age')}</TableCell>
                  <TableCell style={{ width: 100 }}>
                    {t('Administrative Level 2')}
                  </TableCell>
                  <TableCell style={{ width: 100 }} align="left">
                    {t('Similarity Score')}
                  </TableCell>
                  <TableCell style={{ width: 100 }} align="left">
                    {t('Proximity to the Score')}
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {biographicalRows.map((row) => {
                  return (
                    <TableRow key={row.hitId}>
                      <TableCell>
                        <BlackLink to={getIndividualDetailsPath(row.hitId)}>
                          {row.unicefId}
                        </BlackLink>
                      </TableCell>
                      <TableCell align="left">{row.fullName}</TableCell>
                      <TableCell align="left">
                        {row.age || t('Not provided')}
                      </TableCell>
                      <TableCell align="left">{row.location}</TableCell>
                      <TableCell align="left">{row.score}</TableCell>
                      <TableCell align="left">
                        {row.proximityToScore > 0 && '+'} {row.proximityToScore}
                      </TableCell>
                    </TableRow>
                  );
                })}{' '}
              </TableBody>
            </StyledTable>
          </div>
          <div>
            <h3>{t('Biometric')}</h3>
            <StyledTable>
              <TableHead>
                <TableRow>
                  <TableCell style={{ width: 100 }}>
                    {t(`${beneficiaryGroup?.memberLabel} ID`)}
                  </TableCell>
                  <TableCell style={{ width: 100 }}>{t('Full Name')}</TableCell>
                  <TableCell style={{ width: 100 }}>{t('Age')}</TableCell>
                  <TableCell style={{ width: 100 }}>
                    {t('Administrative Level 2')}
                  </TableCell>
                  <TableCell style={{ width: 100 }} align="left">
                    {t('Similarity Score')}
                  </TableCell>
                  <TableCell style={{ width: 100 }} align="left" />
                </TableRow>
              </TableHead>
              <TableBody>
                {biometricSortedRows.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>
                      <BlackLink to={getIndividualDetailsPath(row.id)}>
                        {row.unicefId}
                      </BlackLink>
                    </TableCell>
                    <TableCell align="left">{row.fullName}</TableCell>
                    <TableCell align="left">
                      {row.age || t('Not provided')}
                    </TableCell>
                    <TableCell align="left">{row.location}</TableCell>
                    <TableCell align="left">{row.similarityScore}</TableCell>
                    <TableCell align="left">
                      <BiometricsResultsRdi
                        similarityScore={row.similarityScore}
                        individual1={individual}
                        individual2={row}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </StyledTable>
          </div>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button
              onClick={(e) => {
                setOpen(false);
                e.preventDefault();
                e.stopPropagation();
              }}
            >
              {t('CLOSE')}
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
}
