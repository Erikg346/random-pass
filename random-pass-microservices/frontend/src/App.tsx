import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import PasswordGenerator from './components/PasswordGenerator';

const App: React.FC = () => {
    return (
        <Router>
            <div>
                <h1>Password Management System</h1>
                <Switch>
                    <Route path="/" exact>
                        <h2>Welcome to the Password Management System</h2>
                    </Route>
                    <Route path="/generate-password" component={PasswordGenerator} />
                </Switch>
            </div>
        </Router>
    );
};

export default App;