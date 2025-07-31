import { StatusBox } from '@core/StatusBox';
import { useBaseUrl } from '@hooks/useBaseUrl';
import ArrowDropDown from '@mui/icons-material/ArrowDropDown';
import ClearIcon from '@mui/icons-material/Clear';
import SearchIcon from '@mui/icons-material/Search';
import {
  CircularProgress,
  IconButton,
  InputAdornment,
  TextField,
} from '@mui/material';
import Autocomplete, {
  autocompleteClasses,
  AutocompleteCloseReason,
} from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import ButtonBase from '@mui/material/ButtonBase';
import ClickAwayListener from '@mui/material/ClickAwayListener';
import Popper from '@mui/material/Popper';
import { styled } from '@mui/material/styles';
import { ProgramDetail } from '@restgenerated/models/ProgramDetail';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { programStatusToColor } from '@utils/utils';
import {
  ChangeEvent,
  KeyboardEvent,
  MouseEvent,
  useEffect,
  useRef,
  useState,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { useProgramContext } from '../programContext';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';
import { PaginatedProgramListList } from '@restgenerated/models/PaginatedProgramListList';

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
  // eslint-disable-next-line no-unused-vars
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

export const GlobalProgramSelect = () => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const { businessArea, programId } = useBaseUrl();
  const { selectedProgram, setSelectedProgram } = useProgramContext();
  const navigate = useNavigate();
  const [queryParams, setQueryParams] = useState({});

  const {
    data: programsData,
    isLoading: loadingPrograms,
    refetch: refetchPrograms,
  } = useQuery<PaginatedProgramListList>({
    queryKey: ['businessAreaProgram', businessArea, queryParams],
    queryFn: () =>
      RestService.restBusinessAreasProgramsList({
        businessAreaSlug: businessArea,
        ...queryParams,
      }),
  });

  const isMounted = useRef(false);
  const [inputValue, setInputValue] = useState<string>('');

  const { data: program, isLoading: loadingProgram } = useQuery<ProgramDetail>({
    queryKey: ['businessAreaProgram', businessArea, programId],
    queryFn: () =>
      RestService.restBusinessAreasProgramsRetrieve({
        businessAreaSlug: businessArea,
        slug: programId,
      }),
    enabled: programId !== 'all' && !!programId,
  });
  const [programs, setPrograms] = useState([]);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
    };
  }, []);

  useEffect(() => {
    // Initial setup for selectedProgram
    setSelectedProgram({
      beneficiaryGroup: {
        id: 'default-id',
        name: 'Beneficiaries',
        groupLabel: 'Group',
        groupLabelPlural: 'Groups',
        memberLabel: 'Member',
        memberLabelPlural: 'Members',
        masterDetail: false,
      },
      id: 'all',
      name: 'All Programmes',
      status: ProgramStatusEnum.ACTIVE,
      dataCollectingType: null,
      pduFields: null,
      programmeCode: null,
      slug: null,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (programId !== 'all') {
      if (
        program &&
        isMounted.current &&
        (!selectedProgram || selectedProgram?.slug !== programId)
      ) {
        const {
          id,
          name,
          status,
          dataCollectingType,
          pduFields,
          beneficiaryGroup,
          programmeCode,
          slug,
        } = program;

        setSelectedProgram({
          id,
          name,
          status,
          dataCollectingType,
          pduFields,
          beneficiaryGroup,
          programmeCode,
          slug,
        });
      }
    }
  }, [programId, selectedProgram, setSelectedProgram, program]);

  useEffect(() => {
    // If the programId is not in a valid format or not one of the available programs, redirect to the access denied page
    if (
      programId &&
      programId !== 'all' &&
      !loadingProgram &&
      program === null
    ) {
      setSelectedProgram(null);
      navigate(`/access-denied/${businessArea}`);
    }
  }, [
    programId,
    navigate,
    businessArea,
    loadingProgram,
    program,
    setSelectedProgram,
  ]);

  useEffect(() => {
    if (programsData) {
      const newProgramsList: Partial<ProgramDetail>[] = [];
      if (inputValue === '') {
        newProgramsList.push({
          id: 'all',
          name: 'All Programmes',
          status: null,
          slug: 'all',
        });
      }
      newProgramsList.push(
        ...programsData.results.map(({ id, name, slug, status }) => ({
          id,
          name,
          status,
          slug,
        })),
      );
      setPrograms(newProgramsList);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [programsData, inputValue]);

  const handleClose = () => {
    setAnchorEl(null);
  };

  const onChange = (_event: any, selectedValue: ProgramDetail): void => {
    if (selectedValue) {
      handleClose();
      if (selectedValue.id === 'all') {
        setSelectedProgram({
          beneficiaryGroup: {
            id: 'default-id',
            name: 'Beneficiaries',
            groupLabel: 'Group',
            groupLabelPlural: 'Groups',
            memberLabel: 'Member',
            memberLabelPlural: 'Members',
            masterDetail: false,
          },
          id: 'all',
          name: 'All Programmes',
          status: ProgramStatusEnum.ACTIVE,
          dataCollectingType: null,
          pduFields: null,
          programmeCode: null,
          slug: null,
        });
        navigate(`/${businessArea}/programs/all/list`);
      } else {
        navigate(
          `/${businessArea}/programs/${selectedValue.slug}/details/${selectedValue.slug}`,
        );
      }
    }
  };

  const searchPrograms = () => {
    if (!inputValue) {
      setQueryParams({});
    } else {
      setQueryParams({
        first: 10,
        orderBy: 'name',
        status: [
          ProgramStatusEnum.ACTIVE,
          ProgramStatusEnum.DRAFT,
          ProgramStatusEnum.FINISHED,
        ],
        name: inputValue,
      });
    }
    refetchPrograms();
  };

  const handleClick = (event: MouseEvent<HTMLElement>) => {
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
            onClose={(_event: ChangeEvent, reason: AutocompleteCloseReason) => {
              if (reason === 'escape') {
                handleClose();
              }
            }}
            onChange={onChange}
            slots={{
              popper: PopperComponent,
            }}
            noOptionsText="No results"
            renderOption={(props, option) => {
              const { key, ...restProps } = props;
              return (
                <li key={key} {...restProps}>
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
              );
            }}
            filterOptions={(x) => x}
            options={programs}
            getOptionLabel={(option) => option.name}
            forcePopupIcon={false}
            loading={loadingPrograms}
            inputValue={inputValue}
            renderInput={(params) => (
              <StyledTextField
                {...params}
                placeholder="Search programmes"
                variant="outlined"
                size="small"
                ref={params.InputProps.ref}
                autoFocus
                onChange={handleOnChangeInput}
                onKeyDown={handleEnter}
                onFocus={() => {
                  refetchPrograms();
                }}
                slotProps={{
                  htmlInput: {
                    ...params.inputProps,
                    'data-cy': 'search-input-gpf',
                  },
                  input: {
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {params.InputProps?.endAdornment}
                        <InputAdornment position="end">
                          {loadingPrograms && <CircularProgress />}
                          {inputValue && (
                            <IconButton
                              data-cy="clear-icon"
                              onClick={clearInput}
                            >
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
                  },
                }}
              />
            )}
          />
        </ClickAwayListener>
      </StyledPopper>
    </>
  );
};
