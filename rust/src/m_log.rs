use std::fmt;

use serde_derive::Serialize;

#[derive(Debug, PartialEq, Serialize)]
pub struct Log<'a> {
    pub remote_addr: &'a str,
    pub remote_user: &'a str,
    pub time_local: &'a str,
    pub request: &'a str,
    pub status: &'a str,
    pub body_bytes_sent: &'a str,
    pub http_referer: &'a str,
    pub http_user_agent: &'a str,
}

impl<'a> fmt::Display for Log<'a> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(
            f,
            "{},{},{},{},{},{},{},{}",
            self.remote_addr,
            self.remote_user,
            self.time_local,
            self.request,
            self.status,
            self.body_bytes_sent,
            self.http_referer,
            self.http_user_agent,
        )
    }
}

pub fn get_log(text: &str) -> Option<Log> {
    let mut log_parts_index = vec![0];
    let characters_to_match = vec![
        b' ', b' ', b'[', b']', b'"', b'"', b' ', b' ', b'"', b'"', b'"',
    ];
    let bytes = text.as_bytes();
    let mut match_index = 0;
    for (i, &item) in bytes.iter().enumerate() {
        if item == characters_to_match[match_index] {
            log_parts_index.push(i);
            if match_index < characters_to_match.len() - 1 {
                match_index += 1;
            }
        }
    }
    if log_parts_index.len() == 13 {
        Some(Log {
            remote_addr: &text[log_parts_index[0]..log_parts_index[1]],
            remote_user: &text[log_parts_index[2] + 1..log_parts_index[3] - 1],
            time_local: &text[log_parts_index[3] + 1..log_parts_index[4]],
            request: &text[log_parts_index[5] + 1..log_parts_index[6]],
            status: &text[log_parts_index[7] + 1..log_parts_index[8]],
            body_bytes_sent: &text[log_parts_index[8] + 1..log_parts_index[9] - 1],
            http_referer: &text[log_parts_index[9] + 1..log_parts_index[10]],
            http_user_agent: &text[log_parts_index[11] + 1..log_parts_index[12]],
        })
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_log_for_correct_log() {
        assert_eq!(
            Some(Log{
                remote_addr: "8.8.8.8",
                remote_user: "-",
                time_local: "28/Oct/2021:00:18:22 +0100",
                request: "GET / HTTP/1.1",
                status: "200",
                body_bytes_sent: "77",
                http_referer: "-",
                http_user_agent: "foo bar 1"}
                ),
            get_log("8.8.8.8 - - [28/Oct/2021:00:18:22 +0100] \"GET / HTTP/1.1\" 200 77 \"-\" \"foo bar 1\"")
        );
    }

    #[test]
    fn test_get_log_for_incorrect_log() {
        assert_eq!(
            None,
            get_log("8.8.8.8 - - [28/Oct/2021:00:18:22 +0100 \"GET / HTTP/1.1\" 200 77 \"-\" \"foo bar 1\"")
        );
    }
}
