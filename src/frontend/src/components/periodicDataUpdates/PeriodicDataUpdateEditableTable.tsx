import React from 'react';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import {
  Table,
  TableHead,
  TableRow,
  TableBody,
  TableCell,
  TextField,
  Button,
} from '@mui/material';
import { format } from 'date-fns';
import { Box } from '@mui/system';
import { DatePicker } from '@mui/x-date-pickers';
import { BaseSection } from '@components/core/BaseSection';
import { BlackLink } from '@components/core/BlackLink';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { t } from 'i18next';
import { PduField } from './PeriodicDataUpdatesOnlineEditsTemplateDetailsPage';
import { useBaseUrl } from '@hooks/useBaseUrl';

type Individual = {
  individualUuid?: string;
  unicefId?: string;
  firstName?: string;
  lastName?: string;
  pduFields: { [key: string]: PduField };
};

type PeriodicDataUpdateEditableTableProps = {
  editRows: Individual[];
  setEditRows: React.Dispatch<React.SetStateAction<Individual[]>>;
  editingRows: Set<number>;
  setEditingRows: React.Dispatch<React.SetStateAction<Set<number>>>;
  allPduFields: Array<{
    key: string;
    subtype: string;
    roundNumber?: number;
    roundName?: string;
    fieldName?: string;
    label?: string;
  }>;
  handleSaveRow: (rowIdx: number) => void;
  canSave: boolean;
  templateStatus: string;
  isAuthorized: boolean;
};

const StickyHeaderCell = ({ shouldScroll, children }) => (
  <TableCell
    style={{
      ...(shouldScroll
        ? {
            position: 'sticky',
            top: 0,
            background: '#fff',
            zIndex: 3,
          }
        : {}),
      borderBottom: '1px solid #888',
    }}
  >
    {children}
  </TableCell>
);

const PeriodicDataUpdateEditableTable: React.FC<
  PeriodicDataUpdateEditableTableProps
> = ({
  editRows,
  setEditRows,
  editingRows,
  setEditingRows,
  allPduFields,
  handleSaveRow,
  canSave,
  templateStatus,
  isAuthorized,
}) => {
  const { baseUrl } = useBaseUrl();
  const shouldScroll = editRows.length > 10 || allPduFields.length > 6;
  const TableContent = (
    <Table>
      <TableHead>
        <TableRow
          style={
            shouldScroll
              ? {
                  position: 'sticky',
                  top: 0,
                  zIndex: 2,
                  background: '#fff',
                }
              : {}
          }
        >
          <StickyHeaderCell shouldScroll={shouldScroll}>
            {t('Individual ID')}
          </StickyHeaderCell>
          <StickyHeaderCell shouldScroll={shouldScroll}>
            {t('First Name')}
          </StickyHeaderCell>
          <StickyHeaderCell shouldScroll={shouldScroll}>
            {t('Last Name')}
          </StickyHeaderCell>
          {allPduFields.map((field) => {
            return (
              <StickyHeaderCell shouldScroll={shouldScroll} key={field.key}>
                <div
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    minWidth: 120,
                  }}
                >
                  <span style={{ fontWeight: 600 }}>{field.label}</span>
                  {field.roundNumber && (
                    <span style={{ fontSize: 13, color: '#888' }}>
                      {t('Round')} {field.roundNumber || ''}
                    </span>
                  )}
                  {field.roundName && (
                    <span style={{ fontSize: 11, color: '#888' }}>
                      {field.roundName}
                    </span>
                  )}
                </div>
              </StickyHeaderCell>
            );
          })}
          <StickyHeaderCell shouldScroll={shouldScroll}>
            <></>
          </StickyHeaderCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {editRows.length === 0 ? (
          <TableRow>
            <TableCell colSpan={3 + allPduFields.length} align="center">
              {t('No data available')}
            </TableCell>
          </TableRow>
        ) : (
          editRows.map((individual, idx) => {
            const isEditing = editingRows.has(idx);
            // Only show Edit button if at least one PDU field is editable
            const hasEditableField =
              individual.pduFields &&
              Object.values(individual.pduFields).some(
                (f: any) => f.isEditable,
              );
            return (
              <TableRow key={individual.individualUuid || idx}>
                <TableCell>
                  {individual.individualUuid ? (
                    <BlackLink
                      to={`/${baseUrl}/population/individuals/${individual.individualUuid}`}
                    >
                      {individual.unicefId}
                    </BlackLink>
                  ) : (
                    t('-')
                  )}
                </TableCell>
                <TableCell>{individual.firstName}</TableCell>
                <TableCell>{individual.lastName}</TableCell>
                {allPduFields.map((col) => {
                  const fieldKey = col.fieldName;
                  const field = individual.pduFields
                    ? individual.pduFields[fieldKey]
                    : null;
                  return (
                    <TableCell key={fieldKey} align="center">
                      {field ? (
                        isEditing && field.isEditable ? (
                          field.subtype === 'DATE' ? (
                            <DatePicker
                              value={field.value ? new Date(field.value) : null}
                              onChange={(newValue) => {
                                setEditRows((prev) => {
                                  const updated = [...prev];
                                  const pduFieldsObj = {
                                    ...updated[idx].pduFields,
                                  };
                                  let formattedValue = null;
                                  if (
                                    newValue instanceof Date &&
                                    !isNaN(newValue.getTime())
                                  ) {
                                    formattedValue = format(
                                      newValue,
                                      'yyyy-MM-dd',
                                    );
                                  }
                                  pduFieldsObj[fieldKey] = {
                                    ...pduFieldsObj[fieldKey],
                                    value: formattedValue,
                                  };
                                  updated[idx] = {
                                    ...updated[idx],
                                    pduFields: pduFieldsObj,
                                  };
                                  return updated;
                                });
                              }}
                              format="yyyy-MM-dd"
                              slotProps={{
                                textField: {
                                  fullWidth: true,
                                  inputProps: { mask: '____-__-__' },
                                },
                              }}
                            />
                          ) : field.subtype === 'BOOL' ? (
                            <div
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: 8,
                              }}
                            >
                              <span
                                style={{ cursor: 'pointer' }}
                                title={t('Set YES')}
                                onClick={() => {
                                  setEditRows((prev) => {
                                    const updated = [...prev];
                                    const pduFieldsObj = {
                                      ...updated[idx].pduFields,
                                    };
                                    pduFieldsObj[fieldKey] = {
                                      ...pduFieldsObj[fieldKey],
                                      value: true,
                                    };
                                    updated[idx] = {
                                      ...updated[idx],
                                      pduFields: pduFieldsObj,
                                    };
                                    return updated;
                                  });
                                }}
                              >
                                <CheckIcon
                                  fontSize="small"
                                  style={{
                                    color:
                                      field.value === true ? 'green' : '#ccc',
                                  }}
                                />
                              </span>
                              <span
                                style={{ cursor: 'pointer' }}
                                title={t('Set NO')}
                                onClick={() => {
                                  setEditRows((prev) => {
                                    const updated = [...prev];
                                    const pduFieldsObj = {
                                      ...updated[idx].pduFields,
                                    };
                                    pduFieldsObj[fieldKey] = {
                                      ...pduFieldsObj[fieldKey],
                                      value: false,
                                    };
                                    updated[idx] = {
                                      ...updated[idx],
                                      pduFields: pduFieldsObj,
                                    };
                                    return updated;
                                  });
                                }}
                              >
                                <CloseIcon
                                  fontSize="small"
                                  style={{
                                    color:
                                      field.value === false ? 'red' : '#ccc',
                                  }}
                                />
                              </span>
                              <span
                                style={{ cursor: 'pointer' }}
                                title={t('Clear')}
                                onClick={() => {
                                  setEditRows((prev) => {
                                    const updated = [...prev];
                                    const pduFieldsObj = {
                                      ...updated[idx].pduFields,
                                    };
                                    pduFieldsObj[fieldKey] = {
                                      ...pduFieldsObj[fieldKey],
                                      value: null,
                                    };
                                    updated[idx] = {
                                      ...updated[idx],
                                      pduFields: pduFieldsObj,
                                    };
                                    return updated;
                                  });
                                }}
                              >
                                <CheckBoxOutlineBlankIcon
                                  fontSize="small"
                                  style={{
                                    color:
                                      field.value == null ? '#888' : '#ccc',
                                  }}
                                />
                              </span>
                            </div>
                          ) : (
                            <TextField
                              variant="outlined"
                              fullWidth
                              size="small"
                              type={
                                field.subtype === 'DECIMAL' ? 'number' : 'text'
                              }
                              value={field.value ?? ''}
                              onChange={(e) => {
                                let newValue;
                                if (field.subtype === 'DECIMAL') {
                                  // If input is empty, set to null
                                  newValue =
                                    e.target.value === ''
                                      ? null
                                      : Number(e.target.value);
                                } else {
                                  newValue = e.target.value;
                                }
                                setEditRows((prev) => {
                                  const updated = [...prev];
                                  const pduFieldsObj = {
                                    ...updated[idx].pduFields,
                                  };
                                  pduFieldsObj[fieldKey] = {
                                    ...pduFieldsObj[fieldKey],
                                    value: newValue,
                                  };
                                  updated[idx] = {
                                    ...updated[idx],
                                    pduFields: pduFieldsObj,
                                  };
                                  return updated;
                                });
                              }}
                            />
                          )
                        ) : // Display mode: show value as icon for BOOL, plain text for others
                        field.subtype === 'DATE' ? (
                          field.value ? (
                            <UniversalMoment>{field.value}</UniversalMoment>
                          ) : (
                            <span style={{ color: '#aaa' }}>{t('-')}</span>
                          )
                        ) : field.subtype === 'BOOL' ? (
                          field.value === true ? (
                            <span style={{ color: 'green' }}>
                              <CheckIcon fontSize="small" />
                            </span>
                          ) : field.value === false ? (
                            <span style={{ color: 'red' }}>
                              <CloseIcon fontSize="small" />
                            </span>
                          ) : (
                            <span style={{ color: '#aaa' }}>{t('-')}</span>
                          )
                        ) : field.value !== undefined &&
                          field.value !== null &&
                          field.value !== '' ? (
                          <span>{String(field.value)}</span>
                        ) : (
                          <span style={{ color: '#aaa' }}>{t('-')}</span>
                        )
                      ) : (
                        <span style={{ color: '#aaa' }}>{t('-')}</span>
                      )}
                    </TableCell>
                  );
                })}
                <TableCell>
                  {canSave &&
                    hasEditableField &&
                    templateStatus === 'NEW' &&
                    (isEditing ? (
                      (() => {
                        return (
                          <Button
                            variant="contained"
                            color="primary"
                            size="small"
                            onClick={() => {
                              setEditRows((prev) => {
                                const updated = [...prev];
                                const pduFieldsObj = {
                                  ...updated[idx].pduFields,
                                };
                                allPduFields.forEach((col) => {
                                  const field = pduFieldsObj[col.key];
                                  if (field && field.isEditable) {
                                    // Only set to null for empty strings in text/number fields
                                    if (
                                      (typeof field.value === 'string' &&
                                        field.value.trim() === '') ||
                                      field.value === undefined
                                    ) {
                                      if (field.subtype !== 'BOOL') {
                                        pduFieldsObj[col.key] = {
                                          ...field,
                                          value: null,
                                        };
                                      }
                                    }
                                  }
                                });
                                updated[idx] = {
                                  ...updated[idx],
                                  pduFields: pduFieldsObj,
                                };
                                return updated;
                              });
                              handleSaveRow(idx);
                            }}
                          >
                            {t('Save')}
                          </Button>
                        );
                      })()
                    ) : (
                      <Button
                        variant="outlined"
                        color="primary"
                        size="small"
                        disabled={!isAuthorized}
                        onClick={() =>
                          setEditingRows((prev) => {
                            const updated = new Set(prev);
                            updated.add(idx);
                            return updated;
                          })
                        }
                      >
                        {t('Edit')}
                      </Button>
                    ))}
                </TableCell>
              </TableRow>
            );
          })
        )}
      </TableBody>
    </Table>
  );
  return (
    <Box pt={6}>
      <BaseSection p={0} title="Periodic Data Update">
        <div
          style={{
            width: '100%',
            maxHeight: 800,
            overflow: 'auto',
            border: '1px solid #eee',
          }}
        >
          {TableContent}
        </div>
      </BaseSection>
    </Box>
  );
};

export default PeriodicDataUpdateEditableTable;
