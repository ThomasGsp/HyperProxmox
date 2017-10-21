<?php

class RequestTest extends PHPUnit_Framework_TestCase
{
	public function testPost()
	{
		$_POST["test"] = 22;
		$this->assertEquals(22, Request::post('test'));
		$this->assertEquals(null, Request::post('not_existing_key'));

		// test trim & strip_tags: Method is used with second argument "true", triggering a cleaning of the input
		$_POST["attacker_string"] = '   <script>alert("yo!");</script>   ';
		$this->assertEquals('alert("yo!");', Request::post('attacker_string', true));
	}

	public function testGet()
	{
		$_GET["test"] = 33;
		$this->assertEquals(33, Request::get('test'));
		$this->assertEquals(null, Request::get('not_existing_key'));
	}

	public function testCookie()
	{
		$_COOKIE["test"] = 44;
		$this->assertEquals(44, Request::cookie('test'));
		$this->assertEquals(null, Request::cookie('not_existing_key'));
	}
}
