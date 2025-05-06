import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Navbar from '../components/navigation/Navbar';
import Footer from '../components/navigation/Footer';

const Layout = ({ children }) => {
  return (
    <div>
      <Navbar />
      <ToastContainer
        autoClose={5000}
      />
      {children}
      <Footer />
    </div>
  );
}

export default Layout;