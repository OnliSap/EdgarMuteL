import builtins
import unittest
from unittest.mock import patch

import bot


class ServerStartupTests(unittest.TestCase):
    def test_run_flask_uses_default_host_and_port(self):
        with patch("builtins.print"), patch.object(bot, "app") as mock_app:
            bot.run_flask()
            mock_app.run.assert_called_once_with(host="0.0.0.0", port=8000, debug=False, use_reloader=False)


if __name__ == "__main__":
    unittest.main()
