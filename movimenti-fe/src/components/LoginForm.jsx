import React from "react";
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { Navigate } from "react-router-dom";
import { useState } from "react";
import authenticate from "../queries/authenticate";
import { msg, Trans } from "@lingui/macro";
import { useLingui } from "@lingui/react";
import UserContext from "../contexts/UserContext";
import { useContext } from "react";

const LoginForm = ({logout}) => {
  const { _ } = useLingui();
  const [user, setUser] = useContext(UserContext);
  const [error, setError] = useState(null);
  
  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
        const username = event.target.elements.username.value;
        const password = event.target.elements.password.value;
        const results = await authenticate(username, password);
        results.json().then((jres) => {
            sessionStorage.setItem("authToken", jres.token); 
            setUser(username);
        });
    } catch (error) {
      setError(error);
    }
  };
  if(logout){
    sessionStorage.removeItem("authToken");
    // setUser(null);
    // setError(null);
  }

  return (
    <Container>
      {user && <Navigate to="/" replace={true} />}
      <Row className="justify-content-center">
        <Col className="col-md-6 col-lg-4">
        {error && <p>{error.message}</p>}
        </Col>
      </Row>
      <Row className="justify-content-center">
        <Col className="col-md-6 col-lg-4">
          <Form onSubmit={(event) => handleSubmit(event)}>
            <Form.Group className="mb-3">
              <Form.Label htmlFor="username" hidden>
                <Trans>Username</Trans>
              </Form.Label>
              <Form.Control
                id="username"
                name="username"
                placeholder={_(msg`Username`)}
                type="username"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label htmlFor="password" hidden>
                <Trans>Password</Trans>
              </Form.Label>
              <Form.Control
                id="password"
                name="password"
                placeholder={_(msg`Password`)}
                type="password"
              />
            </Form.Group>
            <Button type="submit"><Trans id="login_form_submit">Submit</Trans></Button>
          </Form>
        </Col>
      </Row>
    </Container>
  );
};

export default LoginForm;
