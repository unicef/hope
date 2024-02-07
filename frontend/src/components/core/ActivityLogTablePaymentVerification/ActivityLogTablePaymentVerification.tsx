import { Paper } from '@mui/material';
import Button from '@mui/material/Button';
import Collapse from '@mui/material/Collapse';
import TablePagination from '@mui/material/TablePagination';
import Typography from '@mui/material/Typography';
import ExpandLessIcon from '@mui/icons-material/ExpandLessRounded';
import ExpandMoreIcon from '@mui/icons-material/ExpandMoreRounded';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentVerificationLogEntryNode } from '../../../__generated__/graphql';
import { headCells } from './headCells';
import { LogRow } from './LogRow';
import { ButtonPlaceHolder, Row } from './TableStyledComponents';

const Table = styled.div`
  display: flex;
  flex-direction: column;
`;

const HeadingCell = styled.div`
  display: flex;
  flex: ${({ weight }) => weight || 1};
  padding: 16px;
  font-size: 12px;
  text-align: left;
  font-weight: 500;
  line-height: 1.43rem;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
  letter-spacing: 0.01071em;
  vertical-align: inherit;
`;

const PaperContainer = styled(Paper)`
  width: 100%;
  padding: ${({ theme }) => theme.spacing(5)}px 0;
  margin-bottom: ${({ theme }) => theme.spacing(5)}px;
`;

const Toolbar = styled.div`
  margin: 0 ${({ theme }) => theme.spacing(6)}px;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
`;

interface ActivityLogTablePaymentVerificationProps {
  logEntries: PaymentVerificationLogEntryNode[];
  totalCount: number;
  rowsPerPage: number;
  page: number;
  onChangePage: (event: unknown, newPage: number) => void;
  onChangeRowsPerPage: (event: React.ChangeEvent<HTMLInputElement>) => void;
}
export function ActivityLogTablePaymentVerification({
  logEntries,
  totalCount,
  rowsPerPage,
  page,
  onChangePage,
  onChangeRowsPerPage,
}: ActivityLogTablePaymentVerificationProps): ReactElement {
  const [expanded, setExpanded] = useState(false);
  const { t } = useTranslation();

  return (
    <PaperContainer>
      <Toolbar>
        <Typography variant="h6">{t('Activity Log')}</Typography>
        <Button
          variant="outlined"
          color="primary"
          endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? 'HIDE' : 'SHOW'}
        </Button>
      </Toolbar>
      <Collapse in={expanded}>
        <Table>
          <Row>
            {headCells.map((item) => (
              <HeadingCell key={item.id} style={{ flex: item.weight || 1 }}>
                {item.label}
              </HeadingCell>
            ))}
            <ButtonPlaceHolder />
          </Row>
          {logEntries.map((value) => (
            <LogRow key={value.id} logEntry={value} />
          ))}
        </Table>
        <TablePagination
          rowsPerPageOptions={[5, 10, 15]}
          component="div"
          count={totalCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={onChangePage}
          onRowsPerPageChange={onChangeRowsPerPage}
        />
      </Collapse>
    </PaperContainer>
  );
}
