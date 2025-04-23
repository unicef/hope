import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TablePagination,
  TableRow,
  Typography,
} from '@mui/material';
import { Delete, Edit } from '@mui/icons-material';
import styled from 'styled-components';
import GreaterThanEqual from '../../../assets/GreaterThanEqual.svg';
import LessThanEqual from '../../../assets/LessThanEqual.svg';
import { TargetingCriteriaRuleObjectType } from '@generated/graphql';
import { Box } from '@mui/system';
import { BlueText } from '@components/grievances/LookUps/LookUpStyles';
import { ReactElement, useEffect, useState } from 'react';
import { Fragment } from 'react/jsx-runtime';
import { t } from 'i18next';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { LabelizedField } from '@components/core/LabelizedField';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { FspChoices } from '@restgenerated/models/FspChoices';

interface CriteriaElementProps {
  alternative?: boolean;
}

const CriteriaElement = styled.div<CriteriaElementProps>`
  width: auto;
  max-width: 380px;
  position: relative;
  border: ${(props) => (props.alternative ? '0' : '2px solid #033f91')};
  border-radius: 3px;
  font-size: 16px;
  background-color: ${(props) =>
    props.alternative ? 'transparent' : '#f7faff'};
  padding: ${({ theme }) => theme.spacing(1)}
    ${({ theme, alternative }) =>
      alternative ? theme.spacing(1) : theme.spacing(17)}
    ${({ theme }) => theme.spacing(1)} ${({ theme }) => theme.spacing(4)};
  margin: ${({ theme }) => theme.spacing(2)} 0;
  p {
    margin: ${({ theme }) => theme.spacing(2)} 0;
    span {
      color: ${(props) => (props.alternative ? '#000' : '#003c8f')};
      font-weight: bold;
    }
  }
`;

const ButtonsContainer = styled.div`
  position: absolute;
  right: 0;
  top: 0;
  button {
    color: #949494;
    padding: 12px 8px;
    svg {
      width: 20px;
      height: 20px;
    }
  }
`;

const MathSign = styled.img`
  width: 20px;
  height: 20px;
  vertical-align: middle;
`;

const CriteriaSetBox = styled.div`
  border: '1px solid #607cab';
  border-radius: 3px;
  padding: 0 ${({ theme }) => theme.spacing(2)};
  margin: ${({ theme }) => theme.spacing(2)} 0;
`;

const PduDataBox = styled(Box)`
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 3px;
  padding: ${({ theme }) => theme.spacing(3)};
  margin: ${({ theme }) => theme.spacing(3)};
`;

const CriteriaField = ({ field, choicesDict, dataCy }): ReactElement => {
  const extractChoiceLabel = (choiceField, argument) => {
    let choices = choicesDict?.[choiceField.fieldName];
    if (!choices) {
      choices = choiceField?.fieldAttribute?.choices;
    }
    return choices?.length
      ? choices.find((each) => each.value === argument)?.labelEn
      : argument;
  };

  const displayValueOrEmpty = (value) => (value ? value : 'Empty');

  let fieldElement;

  switch (field.comparisonMethod) {
    case 'NOT_EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute?.labelEn || field.labelEn}:{' '}
          <span>{displayValueOrEmpty(field.arguments?.[0])}</span>
        </p>
      );
      break;
    case 'RANGE':
      fieldElement = (
        <p>
          {field.fieldAttribute?.labelEn || field.labelEn}:{' '}
          <span>
            {displayValueOrEmpty(field.arguments?.[0])} -{' '}
            {displayValueOrEmpty(field.arguments?.[1])}
          </span>
        </p>
      );
      break;
    case 'EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute?.labelEn || field.labelEn}:{' '}
          {field.isNull === true || field.comparisonMethod === 'IS_NULL' ? (
            <BlueText>{t('Empty')}</BlueText>
          ) : typeof field.arguments?.[0] === 'boolean' ? (
            field.arguments[0] ? (
              <BlueText>{t('Yes')}</BlueText>
            ) : (
              <BlueText>{t('No')}</BlueText>
            )
          ) : (
            <>
              {field.arguments?.[0] != null ? (
                field.arguments[0] === 'Yes' ? (
                  <BlueText>{t('Yes')}</BlueText>
                ) : field.arguments[0] === 'No' ? (
                  <BlueText>{t('No')}</BlueText>
                ) : (
                  <span>{extractChoiceLabel(field, field.arguments[0])}</span>
                )
              ) : (
                <BlueText>{t('Empty')}</BlueText>
              )}
            </>
          )}
        </p>
      );
      break;
    case 'LESS_THAN':
    case 'GREATER_THAN': {
      const isLessThan = field?.type === 'LESS_THAN';
      const MathSignComponent = isLessThan ? LessThanEqual : GreaterThanEqual;
      const altText = isLessThan ? 'less_than' : 'greater_than';
      const displayValue = field.arguments?.[0];

      fieldElement = (
        <p>
          {field.fieldAttribute?.labelEn || field.labelEn}:{' '}
          {displayValue && <MathSign src={MathSignComponent} alt={altText} />}
          <span>{displayValueOrEmpty(displayValue)}</span>
        </p>
      );
      break;
    }
    case 'CONTAINS':
      fieldElement = (
        <p>
          {field.fieldAttribute?.labelEn || field.labelEn}:{' '}
          {field.__typename === 'TargetingCollectorBlockRuleFilterNode'
            ? field.arguments?.map((argument, index) => (
                <Fragment key={index}>
                  <span>
                    {argument === true ? (
                      <BlueText>{t('Yes')}</BlueText>
                    ) : argument === false ? (
                      <BlueText>{t('No')}</BlueText>
                    ) : (
                      displayValueOrEmpty(extractChoiceLabel(field, argument))
                    )}
                  </span>
                  {index !== field.arguments.length - 1 && ', '}
                </Fragment>
              ))
            : field.arguments?.map((argument, index) => (
                <Fragment key={index}>
                  <span>
                    {displayValueOrEmpty(extractChoiceLabel(field, argument))}
                  </span>
                  {index !== field.arguments.length - 1 && ', '}
                </Fragment>
              ))}
        </p>
      );
      break;
    default:
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn}:{' '}
          <span>{displayValueOrEmpty(field.arguments?.[0])}</span>
        </p>
      );
      break;
  }

  return (
    <>
      <div data-cy={dataCy}>{fieldElement}</div>
      {field.fieldAttribute?.type === 'PDU' &&
        (field.pduData || field.fieldAttribute.pduData) && (
          <PduDataBox data-cy="round-number-round-name-display">
            Round {field.roundNumber}
            {(field.pduData || field.fieldAttribute.pduData).roundsNames[
              field.roundNumber - 1
            ] && (
              <>
                {' '}
                (
                {
                  (field.pduData || field.fieldAttribute.pduData).roundsNames[
                    field.roundNumber - 1
                  ]
                }
                )
              </>
            )}
          </PduDataBox>
        )}
    </>
  );
};

interface CriteriaProps {
  rules: [TargetingCriteriaRuleObjectType];
  individualsFiltersBlocks;
  collectorsFiltersBlocks;
  removeFunction?;
  editFunction?;
  isEdit: boolean;
  canRemove: boolean;
  alternative?: boolean;
  allDataFieldsChoicesDict;
  allCollectorFieldsChoicesDict;
  householdIds: string;
  individualIds: string;
  deliveryMechanism;
  financialServiceProvider;
  criteriaIndex: number;
  criteria;
}

export function Criteria({
  rules,
  removeFunction = () => null,
  editFunction = () => null,
  isEdit,
  canRemove,
  allDataFieldsChoicesDict,
  allCollectorFieldsChoicesDict,
  alternative = null,
  individualsFiltersBlocks,
  collectorsFiltersBlocks,
  householdIds,
  individualIds,
  deliveryMechanism,
  financialServiceProvider,
  criteriaIndex,
  criteria,
}: CriteriaProps): ReactElement {
  const { businessArea } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const [deliveryMechanismToDisplay, setDeliveryMechanismToDisplay] =
    useState('');
  const [fspToDisplay, setFspToDisplay] = useState('');
  const { data: availableFspsForDeliveryMechanismData } = useQuery<FspChoices>({
    queryKey: ['businessAreasAvailableFspsForDeliveryMechanisms', businessArea],
    queryFn: () => {
      return RestService.restBusinessAreasAvailableFspsForDeliveryMechanismsRetrieve(
        {
          businessAreaSlug: businessArea,
        },
      );
    },
  });
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const [openHH, setOpenHH] = useState(false);
  const [openIND, setOpenIND] = useState(false);
  const [currentHouseholdIds, setCurrentHouseholdIds] = useState<string[]>([]);
  const [currentIndividualIds, setCurrentIndividualIds] = useState<string[]>(
    [],
  );
  const [pageHH, setPageHH] = useState(0);
  const [rowsPerPageHH, setRowsPerPageHH] = useState(5);
  const [pageIND, setPageIND] = useState(0);
  const [rowsPerPageIND, setRowsPerPageIND] = useState(5);

  useEffect(() => {
    const mappedDeliveryMechanisms =
      availableFspsForDeliveryMechanismData.deliveryMechanism((el) => ({
        name: el.deliveryMechanism.name,
        value: el.deliveryMechanism.code,
      }));

    const deliveryMechanismName =
      deliveryMechanism?.name ||
      mappedDeliveryMechanisms?.find(
        (el) => el.value === criteria.deliveryMechanism,
      )?.name;

    const mappedFsps =
      availableFspsForDeliveryMechanismData.deliveryMechanism
        ?.find(
          (el) =>
            el.deliveryMechanism.code === deliveryMechanism ||
            el.deliveryMechanism.code ===
              mappedDeliveryMechanisms?.find(
                (elem) => elem.value === criteria.deliveryMechanism,
              )?.value,
        )
        ?.fsps.map((el) => ({ name: el.name, value: el.id })) || [];

    const fspName =
      financialServiceProvider?.name ||
      mappedFsps?.find((el) => el.value === criteria.fsp)?.name;

    setDeliveryMechanismToDisplay(deliveryMechanismName);
    setFspToDisplay(fspName);
  }, [
    deliveryMechanism,
    financialServiceProvider,
    availableFspsForDeliveryMechanismData,
    criteria,
  ]);

  if (!availableFspsForDeliveryMechanismData) return null;

  const handleChangePageHH = (_event, newPage) => {
    setPageHH(newPage);
  };

  const handleChangeRowsPerPageHH = (event) => {
    setRowsPerPageHH(parseInt(event.target.value, 10));
    setPageHH(0);
  };

  const handleChangePageIND = (_event, newPage) => {
    setPageIND(newPage);
  };

  const handleChangeRowsPerPageIND = (event) => {
    setRowsPerPageIND(parseInt(event.target.value, 10));
    setPageIND(0);
  };

  const handleOpenHouseholdIds = (ids: string): void => {
    setCurrentHouseholdIds(ids.split(','));
    setOpenHH(true);
  };

  const handleOpenIndividualIds = (ids: string): void => {
    setCurrentIndividualIds(ids.split(','));
    setOpenIND(true);
  };

  const handleClose = (): void => {
    setOpenHH(false);
    setOpenIND(false);
  };
  const adjustedCollectorsFiltersBlocks = collectorsFiltersBlocks.map(
    (block) => ({
      ...block,
      collectorBlockFilters: block.collectorBlockFilters.map((filter) => ({
        ...filter,
        arguments: filter.arguments.map((arg) =>
          arg === true ? 'Yes' : arg === false ? 'No' : arg,
        ),
      })),
    }),
  );

  return (
    <CriteriaElement alternative={alternative} data-cy="criteria-container">
      {deliveryMechanismToDisplay && criteriaIndex === 0 && (
        <Grid container>
          <Grid size={{ xs: 6 }}>
            <LabelizedField
              label={t('Delivery Mechanism')}
              value={deliveryMechanismToDisplay}
            />
          </Grid>
          <Grid size={{ xs: 6 }}>
            <LabelizedField label={t('FSP')} value={fspToDisplay} />
          </Grid>
        </Grid>
      )}
      {householdIds && (
        <div>
          <Typography data-cy="household-ids-modal-title" variant="body1">
            {t(`${beneficiaryGroup?.groupLabel} IDs selected`)}:
          </Typography>
          <BlueText
            onClick={() => handleOpenHouseholdIds(householdIds)}
            style={{ textDecoration: 'underline', cursor: 'pointer' }}
            data-cy="button-household-ids-open"
          >
            {householdIds.split(',').length}
          </BlueText>
        </div>
      )}
      {individualIds && (
        <div>
          <Typography data-cy="individual-ids-modal-title" variant="body1">
            {t(`${beneficiaryGroup?.groupLabel} IDs selected`)}:
          </Typography>
          <BlueText
            onClick={() => handleOpenIndividualIds(individualIds)}
            style={{ textDecoration: 'underline', cursor: 'pointer' }}
            data-cy="button-individual-ids-open"
          >
            {individualIds.split(',').length}
          </BlueText>
        </div>
      )}
      {(rules || []).map((each, index) => (
        <CriteriaField
          choicesDict={allDataFieldsChoicesDict}
          key={index}
          field={each}
          dataCy={`criteria-field-${index}`}
        />
      ))}
      {individualsFiltersBlocks.map(
        (item, index) =>
          item.individualBlockFilters.length > 0 && (
            <CriteriaSetBox
              key={index}
              data-cy={`individuals-criteria-set-box-${index}`}
            >
              {item.individualBlockFilters.map((filter, filterIndex) => (
                <CriteriaField
                  choicesDict={allDataFieldsChoicesDict}
                  key={filterIndex}
                  field={filter}
                  dataCy={`individuals-criteria-field-${filterIndex}`}
                />
              ))}
            </CriteriaSetBox>
          ),
      )}
      {adjustedCollectorsFiltersBlocks.map(
        (item, index) =>
          item.collectorBlockFilters.length > 0 && (
            <CriteriaSetBox
              key={index}
              data-cy={`collectors-criteria-set-box-${index}`}
            >
              {item.collectorBlockFilters.map((filter, filterIndex) => (
                <CriteriaField
                  choicesDict={allCollectorFieldsChoicesDict}
                  key={filterIndex}
                  field={filter}
                  dataCy={`collectors-criteria-field-${filterIndex}`}
                />
              ))}
            </CriteriaSetBox>
          ),
      )}
      {isEdit && (
        <ButtonsContainer>
          <IconButton data-cy="button-edit" onClick={editFunction}>
            <Edit />
          </IconButton>
          {canRemove && (
            <IconButton data-cy="button-remove" onClick={removeFunction}>
              <Delete />
            </IconButton>
          )}
        </ButtonsContainer>
      )}
      <Dialog open={openHH} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {t(`Selected ${beneficiaryGroup?.groupLabelPlural}`)}
        </DialogTitle>
        <DialogContent>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {currentHouseholdIds
                .slice(
                  pageHH * rowsPerPageHH,
                  pageHH * rowsPerPageHH + rowsPerPageHH,
                )
                .map((id, index) => (
                  <TableRow key={index}>
                    <TableCell data-cy={`table-cell-hh-${id}`}>{id}</TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={currentHouseholdIds.length}
            rowsPerPage={rowsPerPageHH}
            page={pageHH}
            onPageChange={handleChangePageHH}
            onRowsPerPageChange={handleChangeRowsPerPageHH}
          />
        </DialogContent>
        <DialogActions>
          <Button data-cy="button-close" color="primary" onClick={handleClose}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={openIND} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>{t('Selected Individuals')}</DialogTitle>
        <DialogContent>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {currentIndividualIds
                .slice(
                  pageIND * rowsPerPageIND,
                  pageIND * rowsPerPageIND + rowsPerPageIND,
                )
                .map((id, index) => (
                  <TableRow key={index}>
                    <TableCell data-cy={`table-cell-ind-${id}`}>{id}</TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
          <TablePagination
            rowsPerPageOptions={[5, 10, 25]}
            component="div"
            count={currentIndividualIds.length}
            rowsPerPage={rowsPerPageIND}
            page={pageIND}
            onPageChange={handleChangePageIND}
            onRowsPerPageChange={handleChangeRowsPerPageIND}
          />
        </DialogContent>
        <DialogActions>
          <Button data-cy="button-close" color="primary" onClick={handleClose}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </CriteriaElement>
  );
}

export default withErrorBoundary(Criteria, 'Criteria');
