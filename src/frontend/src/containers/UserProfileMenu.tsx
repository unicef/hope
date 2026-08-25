import {
  Autocomplete,
  Avatar,
  Button,
  CircularProgress,
  ClickAwayListener,
  Grow,
  MenuItem,
  MenuList,
  Paper,
  Popper,
  TextField,
  Typography,
} from '@mui/material';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import styled from 'styled-components';
import React, {
  KeyboardEvent,
  MouseEvent as ReactMouseEvent,
  ReactElement,
  useEffect,
  useRef,
  useState,
} from 'react';
import { api } from '../api/api';
import { RestService } from '@restgenerated/services/RestService';
import { BusinessArea } from '@restgenerated/models/BusinessArea';
import { Profile } from '@restgenerated/models/Profile';
import { restQueryKey } from '@utils/queryKeys';
import { ApiErrorShape, showApiErrorMessages } from '@utils/utils';
import { formatTooltip } from '@utils/timezone';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useSnackbar } from '@hooks/useSnackBar';

const UserProfileButton = styled(Button)`
  && {
    color: #e3e6e7;
  }
`;
const MenuButtonText = styled.span`
  margin-left: ${({ theme }) => theme.spacing(2)};
`;
const TimezonePickerContainer = styled.li`
  list-style: none;
  padding: 8px 16px;
  min-width: 260px;
`;
const CurrentLocalTime = styled(Typography)`
  && {
    margin-top: 8px;
    font-size: 12px;
    color: #848484;
  }
`;

interface TimezoneOption {
  name: string;
  value: string | null;
}

interface UserProfileMenuProps {
  meData: Profile;
}
export function UserProfileMenu({
  meData,
}: UserProfileMenuProps): ReactElement {
  const queryClient = useQueryClient();
  const { businessArea: businessAreaSlug } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const [open, setOpen] = useState(false);
  const [hasOpenedTimezonePicker, setHasOpenedTimezonePicker] =
    useState(false);
  const anchorRef = useRef<HTMLButtonElement>(null);
  const previousTimezoneRef = useRef<string | null>(meData?.timezone ?? null);
  const [localTimezone, setLocalTimezone] = useState<string | null>(
    meData?.timezone ?? null,
  );
  // return focus to the button when we transitioned from !open -> open
  const prevOpen = useRef(open);
  useEffect(() => {
    if (prevOpen.current === true && open === false) {
      anchorRef.current?.focus();
    }

    prevOpen.current = open;
  }, [open]);

  useEffect(() => {
    setLocalTimezone(meData?.timezone ?? null);
  }, [meData?.timezone]);

  const isGlobalScope = businessAreaSlug === 'global';

  const { data: businessAreaData } = useQuery<BusinessArea>({
    queryKey: restQueryKey(RestService.restBusinessAreasRetrieve, {
      slug: businessAreaSlug,
    }),
    queryFn: () =>
      RestService.restBusinessAreasRetrieve({ slug: businessAreaSlug }),
    enabled: !isGlobalScope,
  });

  const { data: timezoneChoicesData, isLoading: timezoneChoicesLoading } =
    useQuery({
      queryKey: restQueryKey(RestService.restBusinessAreasUsersTimezoneChoicesList, {
        businessAreaSlug,
      }),
      queryFn: () =>
        RestService.restBusinessAreasUsersTimezoneChoicesList({
          businessAreaSlug,
        }),
      enabled: open || hasOpenedTimezonePicker,
      staleTime: Infinity,
    });

  const { mutate: updateTimezone, isPending: timezoneSaving } = useMutation({
    mutationFn: (timezone: string | null) =>
      RestService.restBusinessAreasUsersProfileTimezonePartialUpdate({
        businessAreaSlug,
        requestBody: { timezone },
      }),
    onSuccess: (data) => {
      queryClient.setQueriesData<Profile>(
        {
          queryKey: restQueryKey(
            RestService.restBusinessAreasUsersProfileRetrieve,
          ),
        },
        (previous) =>
          previous
            ? {
                ...previous,
                timezone: data.timezone,
                effectiveTimezone: data.effectiveTimezone,
              }
            : previous,
      );
      queryClient.invalidateQueries({
        queryKey: restQueryKey(
          RestService.restBusinessAreasUsersProfileRetrieve,
        ),
      });
    },
    onError: (error: ApiErrorShape) => {
      setLocalTimezone(previousTimezoneRef.current);
      showApiErrorMessages(error, showMessage);
    },
  });

  const handleToggle = (): void => {
    setOpen((previousOpen) => !previousOpen);
  };

  const handleClearCache = () => {
    queryClient.clear();
    api.cache.clear();
  };

  const handleClose = (event): void => {
    if (
      anchorRef.current &&
      anchorRef.current.contains(event.target as HTMLElement)
    ) {
      return;
    }

    setOpen(false);
  };

  const handleLogout = (event: React.MouseEvent<HTMLAnchorElement>): void => {
    window.location.assign('/api/logout');
    localStorage.removeItem('AUTHENTICATED');
    handleClose(event);
    handleClearCache();
  };

  const handleClearCacheAndReloadWindow = () => {
    handleClearCache();
    window.location.reload();
  };

  function handleListKeyDown(event: React.KeyboardEvent): void {
    if (event.key === 'Tab') {
      event.preventDefault();
      setOpen(false);
    }
  }

  const stopEventPropagation = (
    event: ReactMouseEvent | KeyboardEvent,
  ): void => {
    event.stopPropagation();
  };

  const [now, setNow] = useState<Date>(() => new Date());
  useEffect(() => {
    if (!open) {
      return undefined;
    }
    const interval = setInterval(() => setNow(new Date()), 60 * 1000);
    return () => clearInterval(interval);
  }, [open]);

  if (!meData) {
    return null;
  }

  const inheritanceOption: TimezoneOption = isGlobalScope
    ? { name: 'Use system timezone (UTC)', value: null }
    : {
        name: `Use ${businessAreaData?.name ?? businessAreaSlug} timezone (${businessAreaData?.timezone ?? '...'})`,
        value: null,
      };

  const timezoneOptions: TimezoneOption[] = [
    inheritanceOption,
    ...(timezoneChoicesData?.results ?? []),
  ];

  const selectedTimezoneOption =
    timezoneOptions.find((option) => option.value === localTimezone) ??
    inheritanceOption;

  const handleTimezoneChange = (
    _event: React.SyntheticEvent,
    option: TimezoneOption | null,
  ): void => {
    if (!option) return;
    previousTimezoneRef.current = localTimezone;
    setLocalTimezone(option.value);
    updateTimezone(option.value);
  };

  return (
    <>
      <UserProfileButton
        ref={anchorRef}
        onClick={handleToggle}
        data-cy="menu-user-profile"
      >
        <Avatar alt={meData.email} src="/static/images/avatar/1.jpg" />
        <MenuButtonText> {meData.email}</MenuButtonText>
      </UserProfileButton>
      <Popper
        open={open}
        anchorEl={anchorRef.current}
        role={undefined}
        transition
        disablePortal
      >
        {({ TransitionProps, placement }) => (
          <Grow
            {...TransitionProps}
            style={{
              transformOrigin:
                placement === 'bottom' ? 'center top' : 'center bottom',
            }}
          >
            <Paper>
              <ClickAwayListener onClickAway={handleClose}>
                <MenuList
                  component="ul"
                  autoFocusItem={open}
                  id="menu-list-grow"
                  onKeyDown={handleListKeyDown}
                >
                  <TimezonePickerContainer
                    onClick={stopEventPropagation}
                    onKeyDown={stopEventPropagation}
                  >
                    <Autocomplete
                      options={timezoneOptions}
                      value={selectedTimezoneOption}
                      onChange={handleTimezoneChange}
                      onOpen={() => setHasOpenedTimezonePicker(true)}
                      isOptionEqualToValue={(a, b) => a.value === b.value}
                      getOptionLabel={(option) => option.name}
                      loading={timezoneChoicesLoading}
                      disabled={timezoneSaving}
                      disableClearable
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Timezone"
                          size="small"
                          slotProps={{
                            htmlInput: {
                              ...params.slotProps.htmlInput,
                              'data-cy': 'input-timezone-select',
                            },
                            input: {
                              ...params.slotProps.input,
                              endAdornment: (
                                <>
                                  {timezoneChoicesLoading || timezoneSaving ? (
                                    <CircularProgress size={16} />
                                  ) : null}
                                  {params.slotProps.input?.endAdornment}
                                </>
                              ),
                            },
                          }}
                        />
                      )}
                    />
                    <CurrentLocalTime data-cy="current-local-time">
                      Current local time
                      <br />
                      {formatTooltip(now, meData.effectiveTimezone)}
                      <br />
                      {meData.timezone
                        ? 'Personal timezone preference'
                        : `Inherited from ${businessAreaData?.name ?? businessAreaSlug}`}
                    </CurrentLocalTime>
                  </TimezonePickerContainer>
                  <MenuItem
                    onClick={handleClearCacheAndReloadWindow}
                    data-cy="menu-item-clear-cache"
                  >
                    Clear Cache
                  </MenuItem>
                  <MenuItem
                    href="/api/logout"
                    onClick={handleLogout}
                    data-cy="menu-item-logout"
                  >
                    Logout
                  </MenuItem>
                </MenuList>
              </ClickAwayListener>
            </Paper>
          </Grow>
        )}
      </Popper>
    </>
  );
}
