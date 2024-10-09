import * as React from 'react';
import { styled } from '@mui/material/styles';
import Popper from '@mui/material/Popper';
import ClickAwayListener from '@mui/material/ClickAwayListener';
import ArrowDropDown from '@mui/icons-material/ArrowDropDown';
import Autocomplete, {
  autocompleteClasses,
  AutocompleteCloseReason,
} from '@mui/material/Autocomplete';
import ButtonBase from '@mui/material/ButtonBase';
import Box from '@mui/material/Box';
import {
  CircularProgress,
  IconButton,
  InputAdornment,
  TextField,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { programStatusToColor } from '@utils/utils';
import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useProgramContext } from '../programContext';
import { useNavigate } from 'react-router-dom';
import {
  ProgramStatus,
  useAllProgramsForChoicesLazyQuery,
  useProgramQuery,
} from '@generated/graphql';
import { KeyboardEvent, useEffect, useRef, useState } from 'react';
import ClearIcon from '@mui/icons-material/Clear';

interface PopperComponentProps {
  anchorEl?: any;
  disablePortal?: boolean;
  open: boolean;
}

const StyledAutocompletePopper = styled('div')`
  & .${autocompleteClasses.paper} {
    box-shadow: none;
  }
  & .${autocompleteClasses.listbox} {
    & .${autocompleteClasses.option} {
      min-height: auto;
      align-items: flex-start;
      justify-content: space-between;
      padding: 10px;
      & .status-box-container {
        margin-right: 0;
      }
    }
  }
`;

const PopperComponent = (props: PopperComponentProps) => {
  const { disablePortal, anchorEl, open, ...other } = props;
  return <StyledAutocompletePopper {...other} />;
};

const StyledPopper = styled(Popper)`
  border-radius: 6px;
  width: 300px;
  z-index: ${({ theme }) => theme.zIndex.modal};
  background-color: #fff;
  box-shadow:
    0 5px 5px -3px rgba(0, 0, 0, 0.2),
    0 8px 10px 1px rgba(0, 0, 0, 0.14),
    0 3px 14px 2px rgba(0, 0, 0, 0.12);
`;

const StyledTextField = styled(TextField)`
  padding: 10px;
`;

const Button = styled(ButtonBase)`
  && {
    width: ${({ theme }) => theme.spacing(58)};
    background-color: rgba(104, 119, 127, 0.5);
    color: #e3e6e7;
    border-bottom-width: 0;
    border-radius: 4px;
    height: 40px;
    display: flex;
    justify-content: space-between;
    font-family: Roboto, Helvetica, Arial, sans-serif;
    font-weight: 400;
    font-size: 1rem;
    padding: 0 10px;
  }
  &&:hover {
    background-color: rgba(0, 0, 0, 0.09);
  }
`;

const NameBox = styled(Box)`
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 10px;
`;

const ButtonLabel = styled('span')`
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 10px;
`;

interface ProgramRecord {
  id: string;
  name: string;
  status: string;
}

export const GlobalProgramSelect = () => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const { businessArea, programId } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();
  const navigate = useNavigate();
  const [
    loadProgramsList,
    { data: programsList, loading: loadingProgramsList },
  ] = useAllProgramsForChoicesLazyQuery({
    variables: {
      businessArea,
      first: 10,
      orderBy: 'name',
      status: [ProgramStatus.Active, ProgramStatus.Draft],
    },
    fetchPolicy: 'network-only',
  });
  const isMounted = useRef(false);
  const [inputValue, setInputValue] = useState<string>('');
  const { data: programData, loading: loadingProgram } = useProgramQuery({
    variables: { id: programId },
    skip: programId === 'all' || !programId,
  });
  const [programs, setPrograms] = useState<ProgramRecord[]>([]);

  useEffect(() => {
    void loadProgramsList();
  }, [loadProgramsList]);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  useEffect(() => {
    if (programId !== 'all') {
      const program = programData?.program;
      if (
        program &&
        isMounted.current &&
        (!selectedProgram || selectedProgram?.id !== programId)
      ) {
        const { id, name, status, dataCollectingType } = program;

        setSelectedProgram({
          id,
          name,
          status,
          dataCollectingType: {
            id: dataCollectingType?.id,
            code: dataCollectingType?.code,
            type: dataCollectingType?.type,
            label: dataCollectingType?.label,
            householdFiltersAvailable:
              dataCollectingType?.householdFiltersAvailable,
            individualFiltersAvailable:
              dataCollectingType?.individualFiltersAvailable,
          },
          pduFields: program.pduFields,
        });
      }
    } else {
      setSelectedProgram(null);
    }
  }, [programId, selectedProgram, setSelectedProgram, programData]);

  useEffect(() => {
    // If the programId is not in a valid format or not one of the available programs, redirect to the access denied page
    if (
      programId &&
      programId !== 'all' &&
      !loadingProgram &&
      programData?.program === null
    ) {
      setSelectedProgram(null);
      navigate(`/access-denied/${businessArea}`);
    }
  }, [
    programId,
    navigate,
    businessArea,
    loadingProgram,
    programData,
    setSelectedProgram,
  ]);

  useEffect(() => {
    if (programsList?.allPrograms) {
      const newProgramsList: ProgramRecord[] = [];
      if (inputValue === '') {
        newProgramsList.push({
          id: 'all',
          name: 'All Programmes',
          status: null,
        });
      }
      const { edges } = programsList.allPrograms;
      newProgramsList.push(
        ...edges.map(({ node: { id, name, status } }) => ({
          id,
          name,
          status,
        })),
      );
      setPrograms(newProgramsList);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [programsList?.allPrograms, inputValue]);

  const handleClose = () => {
    setAnchorEl(null);
  };

  const onChange = (_event: any, selectedValue: ProgramRecord): void => {
    if (selectedValue) {
      handleClose();
      if (selectedValue.id === 'all') {
        navigate(`/${businessArea}/programs/all/list`);
      } else {
        navigate(
          `/${businessArea}/programs/${selectedValue.id}/details/${selectedValue.id}`,
        );
      }
    }
  };

  const searchPrograms = () => {
    if (!inputValue) {
      void loadProgramsList();
    } else {
      void loadProgramsList({
        variables: {
          businessArea,
          first: 10,
          orderBy: 'name',
          status: [
            ProgramStatus.Active,
            ProgramStatus.Draft,
            ProgramStatus.Finished,
          ],
          name: inputValue,
        },
        fetchPolicy: 'network-only',
      });
    }
  };

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleOnChangeInput = (event: any) => {
    setInputValue(event.target.value);
  };

  const handleEnter = (event: KeyboardEvent) => {
    if (event.key === 'Enter') {
      searchPrograms();
    }
  };

  const clearInput = () => {
    setInputValue('');
    void loadProgramsList();
  };

  const open = Boolean(anchorEl);
  const id = open ? 'global-program-filter' : undefined;
  const buttonTitle = selectedProgram?.name || 'All Programmes';

  if (loadingProgram) {
    return null;
  }

  return (
    <>
      <Box sx={{ width: 221, fontSize: 13 }}>
        <Button
          disableRipple
          aria-describedby={id}
          onClick={handleClick}
          title={buttonTitle}
          data-cy="global-program-filter"
        >
          <ButtonLabel>{buttonTitle}</ButtonLabel>
          <ArrowDropDown />
        </Button>
      </Box>
      <StyledPopper
        id={id}
        open={open}
        anchorEl={anchorEl}
        placement="bottom-start"
      >
        <ClickAwayListener onClickAway={handleClose}>
          <Autocomplete
            open
            onClose={(
              _event: React.ChangeEvent,
              reason: AutocompleteCloseReason,
            ) => {
              if (reason === 'escape') {
                handleClose();
              }
            }}
            onChange={onChange}
            PopperComponent={PopperComponent}
            noOptionsText="No results"
            renderOption={(props, option) => (
              <li {...props}>
                <NameBox data-cy="select-option-name" title={option.name}>
                  {option.name}
                </NameBox>
                {option.status && (
                  <StatusBox
                    status={option.status}
                    statusToColor={programStatusToColor}
                  />
                )}
              </li>
            )}
            filterOptions={(x) => x}
            options={programs}
            getOptionLabel={(option) => option.name}
            forcePopupIcon={false}
            loading={loadingProgramsList}
            inputValue={inputValue}
            renderInput={(params) => (
              <StyledTextField
                {...params}
                placeholder="Search programmes"
                variant="outlined"
                size="small"
                ref={params.InputProps.ref}
                inputProps={{
                  ...params.inputProps,
                  'data-cy': 'search-input-gpf',
                }}
                autoFocus
                onChange={handleOnChangeInput}
                onKeyDown={handleEnter}
                onFocus={() => loadProgramsList()}
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {params.InputProps.endAdornment}
                      <InputAdornment position="end">
                        {loadingProgramsList && <CircularProgress />}
                        {inputValue && (
                          <IconButton data-cy="clear-icon" onClick={clearInput}>
                            <ClearIcon />
                          </IconButton>
                        )}
                        <IconButton
                          data-cy="search-icon"
                          onClick={searchPrograms}
                        >
                          <SearchIcon />
                        </IconButton>
                      </InputAdornment>
                    </>
                  ),
                }}
              />
            )}
          />
        </ClickAwayListener>
      </StyledPopper>
    </>
  );
};
