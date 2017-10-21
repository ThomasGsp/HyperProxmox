probe default_probe {
  .url                = "/";
  .expected_response  = 200;
  .timeout            = 15s;
  .interval           = 15s;
  .window             = 5;
  .threshold          = 2;
}
