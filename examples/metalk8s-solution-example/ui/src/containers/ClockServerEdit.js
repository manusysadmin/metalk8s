import React from 'react';
import { connect } from 'react-redux';
import styled from 'styled-components';
import { Formik, Form } from 'formik';
import * as Yup from 'yup';
import { withRouter } from 'react-router-dom';
import { injectIntl } from 'react-intl';
import { Button, Input, Breadcrumb } from '@scality/core-ui';
import { padding, fontSize } from '@scality/core-ui/dist/style/theme';
import { isEmpty } from 'lodash';
import semver from 'semver';
import { editClockServerAction } from '../ducks/app/clockServer';
import {
  BreadcrumbContainer,
  BreadcrumbLabel,
  StyledLink
} from '../components/BreadcrumbStyle';
import { isVersionSupported } from '../services/utils';

const CreateClockServerContainter = styled.div`
  height: 100%;
  padding: ${padding.base};
  display: inline-block;
`;

const CreateClockServerLayout = styled.div`
  height: 100%;
  overflow: auto;
  display: inline-block;
  margin-top: ${padding.base};
  form {
    .sc-input {
      margin: ${padding.smaller} 0;
      .sc-input-label {
        width: 150px;
        box-sizing: border-box;
      }
      .sc-select,
      .sc-input-type {
        width: 200px;
        box-sizing: border-box;
      }
    }
  }
`;

const InputLabel = styled.label`
  width: 150px;
  padding: 10px;
  font-size: ${fontSize.base};
  box-sizing: border-box;
`;

const InputContainer = styled.div`
  display: inline-flex;
  align-items: center;
`;

const ActionContainer = styled.div`
  display: flex;
  margin: ${padding.large} 0;
  justify-content: flex-end;

  button {
    margin-left: ${padding.large};
  }
`;

const FormSection = styled.div`
  padding: 0 ${padding.larger};
  display: flex;
  flex-direction: column;
`;

const InputValue = styled.label`
  width: 200px;
  font-weight: bold;
  font-size: ${fontSize.large};
`;

const ClockServerEditForm = props => {
  const { intl, match, clockServers, config, stacks } = props;
  const stack = match.params.name;
  const currentStack = stacks.find(item => item.name === stack);
  const currentStackVersion = currentStack ? currentStack.version : '';
  const clockServer = clockServers.find(cr => cr.name === match.params.id);
  const initialValues = {
    version: clockServer ? clockServer.version : '',
    timezone: clockServer ? clockServer.timezone : '',
    name: clockServer ? clockServer.name : '',
    stack
  };

  const validationSchema = Yup.object().shape({
    version: Yup.string()
      .required()
      .test('is-version-valid', intl.messages.not_valid_version, value =>
        semver.valid(value)
      ),
    timezone: Yup.string().required()
  });

  return (
    <CreateClockServerContainter>
      <BreadcrumbContainer>
        <Breadcrumb
          activeColor={config.theme.brand.secondary}
          paths={[
            <StyledLink to="/stacks">{intl.messages.stacks} </StyledLink>,
            <StyledLink to={`/stacks/${stack}`}>{stack}</StyledLink>,
            <BreadcrumbLabel title={intl.messages.edit_clock_server}>
              {intl.messages.edit_clock_server}
            </BreadcrumbLabel>
          ]}
        />
      </BreadcrumbContainer>
      <CreateClockServerLayout>
        {clockServer ? (
          <Formik
            initialValues={initialValues}
            validationSchema={validationSchema}
            onSubmit={props.editClockServer}
          >
            {formProps => {
              const {
                values,
                touched,
                errors,
                setFieldTouched,
                setFieldValue
              } = formProps;

              //handleChange of the Formik props does not update 'values' when field value is empty
              const handleChange = field => e => {
                const { value, checked, type } = e.target;
                setFieldValue(
                  field,
                  type === 'checkbox' ? checked : value,
                  true
                );
              };
              const handleSelectChange = field => selectedObj => {
                setFieldValue(field, selectedObj.value);
              };
              //get the select item from the object array
              const getSelectedObjectItem = (items, selectedValue) => {
                return items.find(item => item.value === selectedValue);
              };

              //touched is not "always" correctly set
              const handleOnBlur = e => setFieldTouched(e.target.name, true);
              const availableVersions = config.versions
                .filter(isVersionSupported(currentStackVersion))
                .map(item => {
                  return {
                    label: item.version,
                    value: item.version
                  };
                });
              return (
                <Form>
                  <FormSection>
                    <InputContainer>
                      <InputLabel>{intl.messages.name}</InputLabel>
                      <InputValue>{values.name}</InputValue>
                    </InputContainer>

                    <Input
                      label={intl.messages.version}
                      clearable={false}
                      type="select"
                      options={availableVersions}
                      placeholder={intl.messages.select_a_version}
                      noResultsText={intl.messages.not_found}
                      name="version"
                      onChange={handleSelectChange('version')}
                      value={getSelectedObjectItem(
                        availableVersions,
                        values.version
                      )}
                      error={touched.version && errors.version}
                      onBlur={handleOnBlur}
                    />

                    <Input
                      name="timezone"
                      label={intl.messages.timezone}
                      value={values.timezone}
                      onChange={handleChange('timezone')}
                      error={touched.timezone && errors.timezone}
                      onBlur={handleOnBlur}
                    />

                    <ActionContainer>
                      <div>
                        <div>
                          <Button
                            text={intl.messages.cancel}
                            type="button"
                            outlined
                            onClick={() =>
                              props.history.push(`/stacks/${stack}`)
                            }
                          />
                          <Button
                            text={intl.messages.edit}
                            type="submit"
                            disabled={!isEmpty(errors)}
                          />
                        </div>
                      </div>
                    </ActionContainer>
                  </FormSection>
                </Form>
              );
            }}
          </Formik>
        ) : null}
      </CreateClockServerLayout>
    </CreateClockServerContainter>
  );
};

function mapStateToProps(state) {
  return {
    config: state.config,
    clockServers: state.app.clockServer.list,
    stacks: state.app.stack.list
  };
}

const mapDispatchToProps = dispatch => {
  return {
    editClockServer: body => dispatch(editClockServerAction(body))
  };
};

export default injectIntl(
  withRouter(
    connect(
      mapStateToProps,
      mapDispatchToProps
    )(ClockServerEditForm)
  )
);
